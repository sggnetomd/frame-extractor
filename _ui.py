"""Helpers visuais — cores, icones, separadores."""
import sys
import os

# Inicializa colorama no Windows pra ANSI escapes funcionarem
try:
    from colorama import init as _init, Fore, Back, Style
    _init(autoreset=True)
    COLORS_OK = True
except ImportError:
    COLORS_OK = False

    class _Empty:
        def __getattr__(self, name):
            return ""

    Fore = Back = Style = _Empty()

# Garante UTF-8 no stdout do Windows pra emojis renderizarem
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


# ── Icones (UTF-8) ──────────────────────────────────────
OK = "✓"
FAIL = "✗"
WARN = "⚠"
INFO = "i"
ARROW = "→"
BULLET = "•"
DOT = "·"

ICON_DOWNLOAD = "⬇"
ICON_UPLOAD = "⬆"
ICON_FOLDER = "📁"
ICON_FILE = "📄"
ICON_KEY = "🔑"
ICON_GEAR = "⚙"
ICON_CLOCK = "⏱"
ICON_ROCKET = "🚀"
ICON_SEARCH = "🔍"
ICON_PENCIL = "✏"
ICON_VIDEO = "🎬"
ICON_MIC = "🎤"
ICON_GLOBE = "🌐"
ICON_CHART = "📊"
ICON_LIST = "📋"
ICON_LINK = "🔗"
ICON_SPARK = "✨"
ICON_FIRE = "🔥"
ICON_DOOR = "🚪"
ICON_BOOK = "📑"
ICON_BOX = "📦"
ICON_IMAGE = "🖼"


# ── Funcoes de print com cor ─────────────────────────────

def ok(msg):
    print(f"{Fore.GREEN}{OK}{Style.RESET_ALL}  {msg}")


def err(msg):
    print(f"{Fore.RED}{FAIL}{Style.RESET_ALL}  {msg}")


def warn(msg):
    print(f"{Fore.YELLOW}{WARN}{Style.RESET_ALL}  {msg}")


def info(msg):
    print(f"{Fore.CYAN}{INFO}{Style.RESET_ALL}  {msg}")


def dim(msg):
    print(f"{Style.DIM}{msg}{Style.RESET_ALL}")


def bold(msg):
    print(f"{Style.BRIGHT}{msg}{Style.RESET_ALL}")


def hl(text, color="cyan"):
    """Retorna string colorida pra usar inline."""
    c = {
        "red": Fore.RED,
        "green": Fore.GREEN,
        "yellow": Fore.YELLOW,
        "blue": Fore.BLUE,
        "cyan": Fore.CYAN,
        "magenta": Fore.MAGENTA,
        "white": Fore.WHITE,
    }.get(color, Fore.CYAN)
    return f"{c}{text}{Style.RESET_ALL}"


# ── Separadores e blocos ─────────────────────────────────

def hr(char="─", width=60, color=None):
    line = char * width
    if color:
        line = hl(line, color)
    print(line)


def section(title, icon="", color="cyan"):
    """Imprime separador com titulo."""
    print()
    print(hl(f"━━━ {icon} {title} ━━━", color) if icon else hl(f"━━━ {title} ━━━", color))


def step(current, total, title, icon=""):
    """Imprime passo do processo."""
    prefix = hl(f"[{current}/{total}]", "yellow")
    if icon:
        title = f"{icon} {title}"
    print(f"\n{prefix} {hl(title, 'cyan')}")
    hr("─", 60, "cyan")


def banner(title, subtitle=None):
    """Banner caixote no estilo Claude Code install."""
    width = 50
    line_top = "╔" + "═" * (width - 2) + "╗"
    line_bot = "╚" + "═" * (width - 2) + "╝"
    line_mid = "║" + " " * (width - 2) + "║"
    print()
    print(hl(line_top, "cyan"))
    print(hl(line_mid, "cyan"))
    print(hl(f"║  {title.ljust(width - 4)}║", "cyan"))
    if subtitle:
        print(hl(f"║  {Style.DIM}{subtitle.ljust(width - 4)}{Style.RESET_ALL}║", "cyan"))
    print(hl(line_mid, "cyan"))
    print(hl(line_bot, "cyan"))


def kv(key, value, icon=""):
    """Imprime key=value alinhado."""
    if icon:
        key = f"{icon} {key}"
    print(f"  {hl(key + ':', 'cyan'):28} {value}")


def bullet(text, icon=BULLET):
    print(f"  {hl(icon, 'cyan')} {text}")


def numbered_item(num, text, icon=None, default=False):
    marker = hl(f"[{num}]", "yellow")
    icon_str = f" {icon}" if icon else ""
    default_str = hl("  (default)", "green") if default else ""
    print(f"  {marker}{icon_str} {text}{default_str}")
