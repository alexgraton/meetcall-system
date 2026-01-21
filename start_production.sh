#!/bin/bash
# Script para iniciar o Meet Call System em produção no Linux/Mac

echo "Iniciando Meet Call System - Producao..."
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

# Verificar se gunicorn está instalado
if ! python -c "import gunicorn" 2>/dev/null; then
    echo "Gunicorn não está instalado. Instalando..."
    pip install gunicorn
fi

echo ""
echo "========================================"
echo "   Meet Call System - PRODUCAO"
echo "========================================"
echo ""
echo "Servidor rodando em: http://localhost:5000"
echo "Pressione Ctrl+C para parar o servidor"
echo ""

# Iniciar servidor com gunicorn
# -w 4: 4 workers (ajustar conforme CPU disponível)
# -b 0.0.0.0:5000: bind em todas as interfaces na porta 5000
# --access-logfile -: logs de acesso no console
# --error-logfile -: logs de erro no console
gunicorn -w 4 -b 0.0.0.0:5000 --access-logfile - --error-logfile - app:app
