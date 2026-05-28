@echo off
REM run_orca_agent.bat
REM Clique duas vezes neste arquivo para iniciar o OrcaAgent.

cd /d "%~dp0"
if not exist "venv\Scripts\activate.bat" (
    echo Ambiente virtual nao encontrado em venv\Scripts\activate.bat
    pause
    exit /b 1
)

call "venv\Scripts\activate.bat"

if "%ANTHROPIC_API_KEY%"=="" (
    if exist "venv\.env" (
        for /f "usebackq tokens=1* delims==" %%A in ("venv\.env") do (
            if /i "%%~A"=="ANTHROPIC_API_KEY" set "ANTHROPIC_API_KEY=%%~B"
        )
    )
)

if "%ANTHROPIC_API_KEY%"=="" (
    echo A variavel ANTHROPIC_API_KEY nao esta definida.
    echo Defina a chave no Windows ou edite este arquivo para incluir a chave.
    echo.
    echo Para definir permanentemente, use:
    echo setx ANTHROPIC_API_KEY "sk-..."
    pause
    exit /b 1
)

echo Usando ANTHROPIC_API_KEY e iniciando o OrcaAgent...
python app.py
pause
