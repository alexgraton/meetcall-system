#!/bin/bash
# Script para iniciar o Meet Call System

echo "Iniciando Meet Call System..."
echo ""

# Verificar se o ambiente virtual está ativo
if [ -z "$VIRTUAL_ENV" ]; then
    echo "AVISO: Ambiente virtual não detectado!"
    echo "Ativando ambiente virtual..."
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
    elif [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    else
        echo "ERRO: Ambiente virtual não encontrado!"
        echo "Execute: python -m venv .venv"
        exit 1
    fi
fi

echo ""
echo "========================================"
echo "   Meet Call System"
echo "========================================"
echo ""
echo "Servidor rodando em: http://localhost:5000"
echo "Pressione Ctrl+C para parar o servidor"
echo ""

# Iniciar servidor Flask
python app.py
