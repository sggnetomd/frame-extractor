@echo off
rem Instalador do Frame Extractor - rode uma vez (dois cliques).
rem Cria o ambiente Python local (.venv), instala as dependencias e confere o FFmpeg.
rem Nao instala nada fora desta pasta.
setlocal
pushd "%~dp0"
set "RC=1"

echo.
echo  === Frame Extractor - instalacao ===
echo.

rem --- 1. Python -------------------------------------------------
rem Testa rodando de verdade: o "python" da Microsoft Store existe no PATH
rem mas nao e um Python (so abre a loja).
set "PYCMD="
py -3 --version >nul 2>nul && set "PYCMD=py -3"
if not defined PYCMD python --version >nul 2>nul && set "PYCMD=python"
if not defined PYCMD goto :sem_python

rem --- 2. Ambiente local + dependencias --------------------------
if exist ".venv\Scripts\python.exe" goto :deps
echo  [..] Criando o ambiente Python local...
%PYCMD% -m venv .venv
if errorlevel 1 goto :falha_venv

:deps
echo  [..] Instalando as dependencias...
".venv\Scripts\python.exe" -m pip install --quiet --disable-pip-version-check -r requirements.txt
if errorlevel 1 goto :falha_deps
echo  [OK] Python pronto.

rem --- 3. FFmpeg -------------------------------------------------
".venv\Scripts\python.exe" -c "import sys, _ffmpeg; sys.exit(0 if _ffmpeg.available() else 1)"
if errorlevel 1 goto :sem_ffmpeg
echo  [OK] FFmpeg encontrado.
echo.
echo  Tudo certo. Arraste um video em cima do "Extrair Frames.bat".
set "RC=0"
goto :fim

:sem_python
echo  [X] Python nao encontrado.
echo.
echo      Abra o Prompt de Comando e rode:
echo          winget install Python.Python.3.13
echo      ou baixe em https://www.python.org/downloads/
echo      marcando a caixa "Add python.exe to PATH" na primeira tela.
echo.
echo      Depois rode este Instalar.bat de novo.
goto :fim

:falha_venv
echo  [X] Nao consegui criar o ambiente Python (.venv).
goto :fim

:falha_deps
echo  [X] Nao consegui instalar as dependencias. Confira a internet e rode de novo.
goto :fim

:sem_ffmpeg
echo  [X] FFmpeg nao encontrado.
echo.
echo      Abra o Prompt de Comando e rode:
echo          winget install Gyan.FFmpeg
echo.
echo      Depois rode este Instalar.bat de novo.
goto :fim

:fim
echo.
popd
if /i not "%~1"=="nopause" pause
exit /b %RC%
