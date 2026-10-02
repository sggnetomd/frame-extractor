@echo off
rem Arraste um video em cima deste arquivo pra ja carregar no programa,
rem ou de dois cliques pra abrir o menu e digitar o caminho.
setlocal
set "HERE=%~dp0"
set "PY=%HERE%.venv\Scripts\python.exe"
rem Primeira vez: ainda nao tem o ambiente Python, entao instala antes de abrir.
if not exist "%PY%" (
    call "%HERE%Instalar.bat" nopause
    if errorlevel 1 (
        pause
        exit /b 1
    )
)
"%PY%" "%HERE%frame_extractor.py" %1
pause
