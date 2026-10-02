# Frame Extractor

Extrai frames de um vídeo na **qualidade original** — a resolução real do arquivo, não um
print da tela. Você informa um trecho (`1:20` até `1:25`) e ele salva todos os frames
daquele intervalo numa pasta, para você escolher o melhor.

Se o vídeo é 1080p, o frame sai em 1920x1080 de verdade.

```
[1] Extrair intervalo      -> todos os frames entre início e fim
[2] Extrair 1 frame exato  -> um tempo específico
[3] Varredura do vídeo     -> miniaturas a cada N segundos, para achar o momento
```

## Instalar (Windows)

Precisa ter na máquina: **Python 3** e **FFmpeg**. Se não tiver, abra o Prompt de Comando
e rode:

```cmd
winget install Python.Python.3.13
winget install Gyan.FFmpeg
```

Depois:

1. Baixe o projeto: botão verde **Code → Download ZIP** aqui no GitHub, e extraia a pasta.
   (Ou `git clone https://github.com/sggnetomd/frame-extractor.git`.)
2. Dê dois cliques em **`Instalar.bat`**. Ele cria o ambiente Python dentro da própria
   pasta e confere o FFmpeg. Não instala nada fora dela.

## Usar

Arraste o vídeo em cima do **`Extrair Frames.bat`**. O menu abre com o vídeo já carregado.

Os frames vão para a pasta `output/`, que abre sozinha no fim de cada extração.

O passo a passo completo, com os casos de problema, está em [COMO-USAR.md](COMO-USAR.md).

## Mac e Linux

O código Python não depende do Windows, mas os atalhos `.bat` sim, e a ferramenta **só foi
testada no Windows**. Para tentar, com o FFmpeg instalado:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python frame_extractor.py "video.mp4"
```
