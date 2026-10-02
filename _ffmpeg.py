"""Wrapper do ffmpeg/ffprobe — localiza binarios, le infos do video e extrai frames.

Nao usa nenhuma lib pesada: chama ffmpeg/ffprobe via subprocess. So precisa que
o FFmpeg esteja instalado (no PATH ou no caminho tipico do winget).
"""
import os
import re
import shutil
import subprocess
from pathlib import Path

# Caminhos tipicos onde o winget instala o FFmpeg (fallback se nao estiver no PATH)
_WINGET_GLOB = (
    Path(os.environ.get("LOCALAPPDATA", ""))
    / "Microsoft" / "WinGet" / "Packages"
)


def _find_binary(name):
    """Acha ffmpeg/ffprobe: primeiro no PATH, depois no diretorio do winget."""
    found = shutil.which(name)
    if found:
        return found
    exe = name + (".exe" if os.name == "nt" else "")
    if _WINGET_GLOB.exists():
        for cand in _WINGET_GLOB.rglob(exe):
            return str(cand)
    return None


FFMPEG = _find_binary("ffmpeg")
FFPROBE = _find_binary("ffprobe")


def available():
    """True se pelo menos o ffmpeg foi encontrado."""
    return FFMPEG is not None


# ── Tempo ────────────────────────────────────────────────

def parse_time(text):
    """Converte "1:23", "1:23.5", "83", "01:02:03.250" -> segundos (float).

    Retorna None se vazio/invalido.
    """
    if text is None:
        return None
    t = text.strip().replace(",", ".")
    if not t:
        return None
    try:
        parts = t.split(":")
        sec = 0.0
        for p in parts:
            sec = sec * 60 + float(p)
        return sec
    except ValueError:
        return None


def fmt_time(sec):
    """Segundos -> "mm:ss" ou "h:mm:ss" pra exibir."""
    sec = float(sec)
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    if h:
        return f"{h}:{m:02d}:{s:05.2f}"
    return f"{m}:{s:05.2f}"


def slug_time(sec):
    """Segundos -> "01m23s" pra nome de pasta/arquivo."""
    sec = int(round(float(sec)))
    return f"{sec // 60:02d}m{sec % 60:02d}s"


# ── Probe (infos do video) ───────────────────────────────

def probe(video):
    """Retorna dict {duration, width, height, fps} ou {} se falhar."""
    if not FFPROBE:
        return {}
    try:
        out = subprocess.run(
            [
                FFPROBE, "-v", "error",
                "-select_streams", "v:0",
                "-show_entries", "stream=width,height,r_frame_rate:format=duration",
                "-of", "default=noprint_wrappers=1",
                str(video),
            ],
            capture_output=True, text=True, timeout=30,
        ).stdout
    except Exception:
        return {}

    info = {}
    for line in out.splitlines():
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip()
        if k == "width":
            info["width"] = _safe_int(v)
        elif k == "height":
            info["height"] = _safe_int(v)
        elif k == "duration":
            info["duration"] = _safe_float(v)
        elif k == "r_frame_rate":
            info["fps"] = _parse_fps(v)
    return info


def _safe_int(v):
    try:
        return int(v)
    except (ValueError, TypeError):
        return None


def _safe_float(v):
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def _parse_fps(v):
    """r_frame_rate vem como "30000/1001" ou "30/1"."""
    try:
        if "/" in v:
            num, den = v.split("/")
            den = float(den)
            return round(float(num) / den, 3) if den else None
        return float(v)
    except (ValueError, TypeError, ZeroDivisionError):
        return None


# ── Extracao ─────────────────────────────────────────────

def _fmt_args(fmt):
    """Retorna (extensao, args_de_qualidade) pro formato escolhido."""
    if fmt == "jpg":
        return "jpg", ["-q:v", "2"]
    return "png", ["-q:v", "1"]


def _run(cmd):
    """Roda o ffmpeg silencioso; retorna (ok, stderr)."""
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode == 0, proc.stderr


def extract_interval(video, start_sec, dur_sec, out_dir, fmt="png"):
    """Extrai TODOS os frames entre start e start+dur. Retorna nº de frames."""
    ext, qargs = _fmt_args(fmt)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    pattern = str(out_dir / f"frame_%04d.{ext}")
    cmd = [
        FFMPEG, "-hide_banner", "-loglevel", "error",
        "-ss", f"{start_sec:.3f}",
        "-i", str(video),
        "-t", f"{dur_sec:.3f}",
        *qargs, "-fps_mode", "passthrough",
        pattern,
    ]
    ok, stderr = _run(cmd)
    if not ok:
        raise RuntimeError(stderr.strip() or "ffmpeg falhou")
    return len(list(out_dir.glob(f"frame_*.{ext}")))


def extract_single(video, t_sec, out_path, fmt="png"):
    """Extrai 1 frame no tempo exato. Retorna o Path do arquivo."""
    ext, qargs = _fmt_args(fmt)
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
        "-ss", f"{t_sec:.3f}",
        "-i", str(video),
        "-frames:v", "1",
        *qargs,
        str(out_path),
    ]
    ok, stderr = _run(cmd)
    if not ok:
        raise RuntimeError(stderr.strip() or "ffmpeg falhou")
    return out_path


def extract_scan(video, every_sec, out_dir, fmt="jpg"):
    """Varredura: 1 frame a cada `every_sec` do video inteiro.

    Nomeia os arquivos pelo tempo (ex: scan_00m05s.jpg) pra facilitar achar
    o momento. Retorna nº de frames.
    """
    ext, qargs = _fmt_args(fmt)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    # fps = 1/every_sec  (ex: 1 frame a cada 5s -> fps=0.2)
    fps_expr = f"1/{every_sec}"
    # %{...} do drawtext seria complexo; nomeamos sequencial e o indice*every = tempo
    pattern = str(out_dir / f"scan_%04d.{ext}")
    cmd = [
        FFMPEG, "-hide_banner", "-loglevel", "error",
        "-i", str(video),
        "-vf", f"fps={fps_expr}",
        *qargs,
        pattern,
    ]
    ok, stderr = _run(cmd)
    if not ok:
        raise RuntimeError(stderr.strip() or "ffmpeg falhou")

    # Renomeia scan_0001 -> scan_00m00s, scan_0002 -> scan_00m05s, etc.
    files = sorted(out_dir.glob(f"scan_[0-9]*.{ext}"))
    renamed = 0
    for idx, f in enumerate(files):
        t = idx * every_sec
        target = out_dir / f"scan_{slug_time(t)}.{ext}"
        try:
            if f.resolve() != target.resolve():
                f.rename(target)
            renamed += 1
        except OSError:
            renamed += 1
    return renamed
