#!/usr/bin/env python3
"""
Frame Extractor - Menu interativo

Extrai frames de um video na QUALIDADE ORIGINAL (resolucao real do arquivo,
sem print de tela). Voce fala um intervalo e ele cospe todos os frames daquele
trecho pra voce escolher o melhor.

Uso:
  python frame_extractor.py                 (abre o menu)
  python frame_extractor.py "video.mp4"     (ja carrega o video / drag-and-drop)
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
_VENV_PY_WIN = _ROOT / ".venv" / "Scripts" / "python.exe"
_VENV_PY_UNIX = _ROOT / ".venv" / "bin" / "python"


def _in_venv():
    here = Path(sys.executable).resolve()
    for cand in (_VENV_PY_WIN, _VENV_PY_UNIX):
        if cand.exists() and here == cand.resolve():
            return True
    return False


if not _in_venv():
    target = _VENV_PY_WIN if _VENV_PY_WIN.exists() else (
        _VENV_PY_UNIX if _VENV_PY_UNIX.exists() else None
    )
    if target:
        import subprocess
        result = subprocess.run([str(target), str(Path(__file__).resolve())] + sys.argv[1:])
        sys.exit(result.returncode)
    else:
        print()
        print("[!] venv nao encontrado. No Windows, de dois cliques no Instalar.bat.")
        print("    Ou rode na mao (uma vez):")
        print()
        print(f"    cd {_ROOT}")
        print("    python -m venv .venv")
        print("    .venv\\Scripts\\python.exe -m pip install -r requirements.txt")
        print()
        sys.exit(1)


import os
import subprocess
from datetime import datetime

import _env_loader  # carrega .env (opcional)  # noqa: F401
import _ui as ui
import _ffmpeg as ff

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "output"
OUTPUT.mkdir(exist_ok=True)

# Video "carregado" na sessao (via drag-and-drop ou opcao de trocar)
CURRENT_VIDEO = None


# ----------------- helpers -----------------

def banner():
    ui.banner("Frame Extractor", "Extrai frames do video na qualidade original")

    using_venv = ".venv" in str(sys.executable).replace("/", "\\")
    if using_venv:
        ui.ok("Python venv ativo")
    else:
        ui.warn(f"venv nao encontrado em {ROOT / '.venv'}")

    if ff.available():
        ui.ok("FFmpeg encontrado")
    else:
        ui.err("FFmpeg NAO encontrado — instale com: winget install Gyan.FFmpeg")

    if CURRENT_VIDEO:
        ui.ok(f"Video: {ui.hl(Path(CURRENT_VIDEO).name, 'yellow')}")
        _print_probe(CURRENT_VIDEO)
    else:
        ui.dim(f"   {ui.DOT} nenhum video carregado (opcao [4] ou arraste um video no .bat)")

    ui.kv("saida", str(OUTPUT), icon=ui.ICON_FOLDER)
    print()


def _print_probe(video):
    info = ff.probe(video)
    if not info:
        return
    dur = info.get("duration")
    w, h = info.get("width"), info.get("height")
    fps = info.get("fps")
    parts = []
    if w and h:
        parts.append(f"{w}x{h}")
    if fps:
        parts.append(f"{fps} fps")
    if dur:
        parts.append(f"duracao {ff.fmt_time(dur)}")
    if parts:
        ui.dim(f"   {ui.DOT} " + "  ".join(parts))


def _ask_video():
    """Garante que tem um video carregado; se nao, pede o caminho."""
    global CURRENT_VIDEO
    if CURRENT_VIDEO and Path(CURRENT_VIDEO).exists():
        return CURRENT_VIDEO
    raw = input(f"{ui.hl(ui.ARROW, 'yellow')} Caminho do video: ").strip().strip('"')
    if not raw:
        return None
    p = Path(raw)
    if not p.exists():
        ui.err(f"Arquivo nao encontrado: {raw}")
        return None
    CURRENT_VIDEO = str(p.resolve())
    return CURRENT_VIDEO


def _ask_format():
    """Pergunta PNG ou JPG. Retorna 'png' ou 'jpg'."""
    ui.dim(f"   Formato: [1] PNG (sem perda)   [2] JPG (menor, quase igual)")
    ch = input(f"{ui.hl(ui.ARROW, 'yellow')} Escolha [Enter=PNG]: ").strip()
    return "jpg" if ch == "2" else "png"


def _open_folder(path):
    try:
        if os.name == "nt":
            os.startfile(str(path))  # noqa
        elif sys.platform == "darwin":
            subprocess.run(["open", str(path)])
        else:
            subprocess.run(["xdg-open", str(path)])
    except Exception as e:
        ui.warn(f"nao consegui abrir a pasta: {e}")


# ----------------- comandos -----------------

def cmd_intervalo():
    ui.section("Extrair intervalo", icon=ui.ICON_VIDEO)
    video = _ask_video()
    if not video:
        return
    _print_probe(video)
    ui.dim("   Tempo no formato mm:ss ou hh:mm:ss (decimais ok: 1:23.5)")
    start = ff.parse_time(input(f"{ui.hl(ui.ARROW, 'yellow')} Inicio: ").strip())
    end = ff.parse_time(input(f"{ui.hl(ui.ARROW, 'yellow')} Fim:    ").strip())
    if start is None or end is None or end <= start:
        ui.err("Intervalo invalido (o fim tem que ser maior que o inicio).")
        return
    dur = end - start
    fmt = _ask_format()

    name = Path(video).stem
    stamp = f"{ff.slug_time(start)}-{ff.slug_time(end)}"
    out_dir = OUTPUT / f"{name}_{stamp}"

    ui.info(f"Extraindo frames de {ff.fmt_time(start)} ate {ff.fmt_time(end)} ({dur:.2f}s)...")
    try:
        n = ff.extract_interval(video, start, dur, out_dir, fmt)
    except RuntimeError as e:
        ui.err(f"ffmpeg: {e}")
        return
    ui.ok(f"{n} frames extraidos em: {ui.hl(str(out_dir), 'green')}")
    _open_folder(out_dir)


def cmd_frame_exato():
    ui.section("Extrair 1 frame exato", icon=ui.ICON_IMAGE)
    video = _ask_video()
    if not video:
        return
    _print_probe(video)
    ui.dim("   Tempo no formato mm:ss ou hh:mm:ss (decimais ok: 1:23.5)")
    t = ff.parse_time(input(f"{ui.hl(ui.ARROW, 'yellow')} Tempo: ").strip())
    if t is None:
        ui.err("Tempo invalido.")
        return
    fmt = _ask_format()

    name = Path(video).stem
    out = OUTPUT / f"{name}_{ff.slug_time(t)}.{fmt}"
    ui.info(f"Extraindo frame em {ff.fmt_time(t)}...")
    try:
        path = ff.extract_single(video, t, out, fmt)
    except RuntimeError as e:
        ui.err(f"ffmpeg: {e}")
        return
    ui.ok(f"Frame salvo: {ui.hl(str(path), 'green')}")
    _open_folder(path.parent)


def cmd_varredura():
    ui.section("Varredura do video (achar o momento)", icon=ui.ICON_SEARCH)
    ui.dim("   Gera 1 miniatura a cada N segundos do video INTEIRO, nomeadas pelo")
    ui.dim("   tempo (scan_01m20s.jpg). Use pra achar onde esta o frame quando o")
    ui.dim("   player nao mostra o tempo. Depois use a opcao [1] no trecho certo.")
    video = _ask_video()
    if not video:
        return
    _print_probe(video)
    raw = input(f"{ui.hl(ui.ARROW, 'yellow')} 1 frame a cada quantos segundos? [Enter=5]: ").strip()
    try:
        every = float(raw.replace(",", ".")) if raw else 5.0
    except ValueError:
        every = 5.0
    if every <= 0:
        ui.err("Valor invalido.")
        return

    name = Path(video).stem
    out_dir = OUTPUT / f"{name}_varredura_{int(every)}s"
    ui.info(f"Varrendo o video (1 frame a cada {every:g}s)...")
    try:
        n = ff.extract_scan(video, every, out_dir, fmt="jpg")
    except RuntimeError as e:
        ui.err(f"ffmpeg: {e}")
        return
    ui.ok(f"{n} miniaturas em: {ui.hl(str(out_dir), 'green')}")
    ui.dim("   Ache o momento pelo nome do arquivo (scan_MMmSSs), depois use [1].")
    _open_folder(out_dir)


def cmd_trocar_video():
    global CURRENT_VIDEO
    ui.section("Carregar / trocar video", icon=ui.ICON_FILE)
    raw = input(f"{ui.hl(ui.ARROW, 'yellow')} Caminho do video: ").strip().strip('"')
    if not raw:
        return
    p = Path(raw)
    if not p.exists():
        ui.err(f"Arquivo nao encontrado: {raw}")
        return
    CURRENT_VIDEO = str(p.resolve())
    ui.ok(f"Video carregado: {Path(CURRENT_VIDEO).name}")


def cmd_abrir_saida():
    _open_folder(OUTPUT)
    ui.ok(f"Abrindo {OUTPUT}")


# ----------------- menu -----------------

def menu():
    print()
    ui.section("MENU PRINCIPAL", icon=ui.ICON_LIST)
    ui.numbered_item("1", f"Extrair intervalo       {ui.DOT} todos os frames entre inicio e fim", ui.ICON_VIDEO)
    ui.numbered_item("2", f"Extrair 1 frame exato   {ui.DOT} um tempo especifico", ui.ICON_IMAGE)
    ui.numbered_item("3", f"Varredura do video      {ui.DOT} miniaturas pra achar o momento", ui.ICON_SEARCH)
    ui.numbered_item("4", f"Carregar/trocar video   {ui.DOT} define o video da sessao", ui.ICON_FILE)
    ui.numbered_item("5", f"Abrir pasta de saida    {ui.DOT} explorer", ui.ICON_FOLDER)
    ui.numbered_item("0", f"Sair", ui.ICON_DOOR)


HANDLERS = {
    "1": cmd_intervalo,
    "2": cmd_frame_exato,
    "3": cmd_varredura,
    "4": cmd_trocar_video,
    "5": cmd_abrir_saida,
}


def main():
    global CURRENT_VIDEO
    # drag-and-drop: primeiro argumento eh o video
    if len(sys.argv) > 1:
        cand = Path(sys.argv[1].strip('"'))
        if cand.exists():
            CURRENT_VIDEO = str(cand.resolve())

    while True:
        banner()
        menu()
        try:
            print()
            choice = input(f"{ui.hl(ui.ARROW, 'yellow')} Escolha [0-5]: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if choice == "0":
            ui.info("Ate mais!")
            break
        h = HANDLERS.get(choice)
        if not h:
            ui.err(f"Opcao invalida: {choice!r}")
            continue
        try:
            h()
        except KeyboardInterrupt:
            ui.warn("Cancelado pelo usuario")
        input(f"\n{ui.hl(ui.DOT, 'cyan')} Enter pra voltar ao menu...")


if __name__ == "__main__":
    main()
