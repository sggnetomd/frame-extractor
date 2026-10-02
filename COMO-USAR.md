# Frame Extractor — Como Usar

Extrai frames de um video na **qualidade original** (a resolucao real do arquivo,
sem print de tela). Voce fala um intervalo e ele cospe todos os frames daquele
trecho numa pasta pra voce escolher o melhor (a melhor expressao, o frame mais
nitido, etc.).

> Resolve o problema do print do CapCut: o print captura a TELA (menor + comprimido).
> Aqui o frame sai no pixel exato do video — se o video eh 1080p, o frame eh
> 1920x1080 de verdade.

## Abrir o programa

Dois jeitos:

1. **Arrastar o video**: arraste o arquivo de video em cima do
   **`Extrair Frames.bat`** — ja abre com o video carregado. (Dois cliques no
   `.bat` tambem abre, e ai voce digita o caminho do video.)
2. **Manual**: abra o cmd na pasta do projeto e rode
   ```cmd
   .venv\Scripts\python.exe frame_extractor.py
   ```

---

## Menu

```
[1] Extrair intervalo      -> todos os frames entre inicio e fim
[2] Extrair 1 frame exato  -> um tempo especifico
[3] Varredura do video     -> miniaturas pra achar o momento
[4] Carregar/trocar video  -> define o video da sessao
[5] Abrir pasta de saida   -> explorer
[0] Sair
```

---

## O fluxo normal

1. Carrega o video (arrasta no `.bat`, ou opcao [4], ou digita o caminho).
2. Opcao **[1] Extrair intervalo**.
3. Digita **Inicio** e **Fim** no formato `mm:ss` (ex: `1:20` ate `1:25`).
   Pode usar decimais pra precisao: `1:23.5`.
4. Escolhe **PNG** (sem perda) ou **JPG** (menor, quase igual) — Enter = PNG.
5. Ele extrai todos os frames do trecho, salva numa pasta em `output/` e
   **abre a pasta**. Voce passa o olho e pega o melhor.

> Num video 30fps, 5 segundos = ~150 imagens. Trechos de 2-4s costumam ser o
> ideal pra nao virar arquivo demais.

---

## "O player nao mostra o tempo do frame"

Esse eh o caso do player **Filmes e TV** do Windows. Use a **[3] Varredura**:

- Ele gera 1 miniatura a cada N segundos do video INTEIRO (default 5s),
  nomeadas pelo tempo: `scan_00m05s.jpg`, `scan_00m10s.jpg`...
- Voce abre a pasta, acha visualmente o momento certo (ex: ta perto do
  `scan_01m20s.jpg`), e ai volta na **[1]** e extrai o intervalo `1:18` a `1:23`
  em qualidade cheia.

---

## Primeira vez (instalar)

De dois cliques no **`Instalar.bat`**. Ele cria o ambiente Python local
(`.venv`), instala as dependencias e confere se o FFmpeg esta na maquina. Nao
mexe em nada fora da pasta do projeto.

Precisa ter antes: **Python 3** e **FFmpeg**. Se faltar algum, o instalador
avisa e mostra o comando:

```cmd
winget install Python.Python.3.13
winget install Gyan.FFmpeg
```

Na mao, se preferir (cmd aberto na pasta do projeto):

```cmd
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

---

## Saida

Tudo vai pra `output/`:

```
output/
  meuvideo_01m20s-01m25s/      <- intervalo: frame_0001.png, frame_0002.png...
  meuvideo_02m03s.png          <- frame exato
  meuvideo_varredura_5s/       <- varredura: scan_00m00s.jpg, scan_00m05s.jpg...
```

---

## Arquivos do projeto

| Arquivo | Pra que serve |
|---|---|
| `frame_extractor.py` | menu principal — sempre roda esse |
| `_ffmpeg.py` | wrapper do ffmpeg/ffprobe (probe + extracao) |
| `_ui.py` | helpers visuais (cores, icones, banner) |
| `_env_loader.py` | carrega .env (opcional) |
| `requirements.txt` | dependencias Python |
| `Extrair Frames.bat` | atalho drag-and-drop |
| `Instalar.bat` | instalacao da primeira vez |
| `output/` | saidas (gitignored) |

---

## Quando da problema

### `FFmpeg NAO encontrado`
Instala com `winget install Gyan.FFmpeg` e reabre o cmd (pra recarregar o PATH).

### Frame saiu preto ou no momento errado
FFmpeg busca o keyframe mais proximo quando o seek eh rapido. Pra tempo cravado,
use a **[1] Extrair intervalo** com um trecho curto em volta do momento — ali
todos os frames sao decodificados com precisao.

### JPG vs PNG
- **PNG**: sem perda nenhuma, arquivo maior. Use se for editar/ampliar.
- **JPG**: bem menor, qualidade 2 (quase indistinguivel). Use pra thumbnail/print.

---

## Stack

- **Python 3.13** + venv local
- **ffmpeg/ffprobe** — extracao no pixel original (via subprocess, sem lib pesada)
- **colorama** — saida colorida no terminal Windows
