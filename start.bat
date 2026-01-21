@echo off
REM Script para iniciar o Meet Call System

echo Iniciando Meet Call System...
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

echo.
echo ========================================
echo   Meet Call System
echo ========================================
echo.
echo Servidor rodando em: http://localhost:5000
echo Pressione Ctrl+C para parar o servidor
echo.

REM Iniciar servidor Flask
python app.py
