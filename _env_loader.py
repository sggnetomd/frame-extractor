"""Carrega .env da pasta do projeto (opcional).

Expoe flags pro frame_extractor.py poder mostrar diagnostico:
  DOTENV_OK     - True se python-dotenv carregou (ou se .env nao existe — ok)
  DOTENV_ERROR  - mensagem de erro se python-dotenv falhou
  ENV_FILE      - Path do arquivo .env esperado
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ENV_FILE = ROOT / ".env"

DOTENV_OK = False
DOTENV_ERROR = None

try:
    from dotenv import load_dotenv

    if ENV_FILE.exists():
        load_dotenv(ENV_FILE, override=False)
    DOTENV_OK = True
except ImportError:
    DOTENV_ERROR = "python-dotenv nao instalado (pip install python-dotenv)"
except Exception as e:
    DOTENV_ERROR = f"erro ao carregar .env: {e}"
