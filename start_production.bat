@echo off
REM Script para iniciar o Meet Call System em produção no Windows

echo Iniciando Meet Call System - Producao...
echo.

REM Verificar se o ambiente virtual está ativo
if not defined VIRTUAL_ENV (
    echo AVISO: Ambiente virtual não detectado!
    echo Ativando ambiente virtual...
    if exist .venv\Scripts\activate.bat (
        call .venv\Scripts\activate.bat
    ) else if exist venv\Scripts\activate.bat (
        call venv\Scripts\activate.bat
    ) else (
        echo ERRO: Ambiente virtual não encontrado!
        echo Execute: python -m venv .venv
        pause
        exit /b 1
    )
)

REM Verificar se waitress está instalado
python -c "import waitress" 2>nul
if errorlevel 1 (
    echo Waitress não está instalado. Instalando...
    pip install waitress
)

echo.
echo ========================================
echo   Meet Call System - PRODUCAO
echo ========================================
echo.
echo Servidor rodando em: http://localhost:5000
echo Pressione Ctrl+C para parar o servidor
echo.

REM Iniciar servidor com waitress
waitress-serve --host=0.0.0.0 --port=5000 app:app
