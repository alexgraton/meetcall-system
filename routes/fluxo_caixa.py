"""
Rotas para Fluxo de Caixa
Visualização consolidada de entradas e saídas financeiras
"""

from flask import Blueprint, render_template, request, jsonify
from models.fluxo_caixa import FluxoCaixaModel
from models.filial import FilialModel
from datetime import datetime, timedelta
from decimal import Decimal

fluxo_caixa_bp = Blueprint('fluxo_caixa', __name__, url_prefix='/fluxo_caixa')

@fluxo_caixa_bp.route('/')
def index():
    """Página principal do fluxo de caixa"""
    
    # Capturar filtros
    data_inicio_str = request.args.get('data_inicio')
    data_fim_str = request.args.get('data_fim')
    filial_id = request.args.get('filial_id')
    conta_bancaria_id = request.args.get('conta_bancaria_id')
    
    # Definir período padrão (30 dias - 15 para trás, 15 para frente)
    hoje = datetime.now().date()
    
    if data_inicio_str:
        data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
    else:
        data_inicio = hoje - timedelta(days=15)
    
    if data_fim_str:
        data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
    else:
        data_fim = hoje + timedelta(days=15)
    
    filial_id = int(filial_id) if filial_id else None
    conta_bancaria_id = int(conta_bancaria_id) if conta_bancaria_id else None
    
    # Buscar dados
    movimentacoes = FluxoCaixaModel.get_movimentacoes(data_inicio, data_fim, filial_id, conta_bancaria_id)
    saldo_inicial = FluxoCaixaModel.get_saldo_inicial(data_inicio, filial_id, conta_bancaria_id)
    projecao_diaria = FluxoCaixaModel.get_projecao_diaria(data_inicio, data_fim, filial_id, conta_bancaria_id)
    
    # Buscar filiais e contas bancárias para filtros
    filiais = FilialModel.get_all()
    from models.conta_bancaria import ContaBancariaModel
    contas_bancarias = ContaBancariaModel.get_all({'ativo': True})
    
    return render_template(
        'fluxo_caixa/index.html',
        movimentacoes=movimentacoes,
        saldo_inicial=saldo_inicial,
        projecao_diaria=projecao_diaria,
        filiais=filiais,
        contas_bancarias=contas_bancarias,
        filtros={
            'data_inicio': data_inicio,
            'data_fim': data_fim,
            'filial_id': filial_id,
            'conta_bancaria_id': conta_bancaria_id
        }
    )

@fluxo_caixa_bp.route('/api/projecao')
def api_projecao():
    """API para retornar dados de projeção em JSON (para gráficos)"""
    
    data_inicio_str = request.args.get('data_inicio')
    data_fim_str = request.args.get('data_fim')
    filial_id = request.args.get('filial_id')
    conta_bancaria_id = request.args.get('conta_bancaria_id')
    
    hoje = datetime.now().date()
    
    if data_inicio_str:
        data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
    else:
        data_inicio = hoje - timedelta(days=15)
    
    if data_fim_str:
        data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
    else:
        data_fim = hoje + timedelta(days=15)
    
    filial_id = int(filial_id) if filial_id else None
    conta_bancaria_id = int(conta_bancaria_id) if conta_bancaria_id else None
    
    projecao = FluxoCaixaModel.get_projecao_diaria(data_inicio, data_fim, filial_id, conta_bancaria_id)
    
    # Converter para formato JSON-friendly
    dados = {
        'labels': [p['data'].strftime('%d/%m') for p in projecao],
        'saldos': [float(p['saldo']) for p in projecao],
        'entradas': [float(p['entradas']) for p in projecao],
        'saidas': [float(p['saidas']) for p in projecao]
    }
    
    return jsonify(dados)

@fluxo_caixa_bp.route('/api/resumo')
def api_resumo():
    """API para retornar resumo do período em JSON"""
    
    data_inicio_str = request.args.get('data_inicio')
    data_fim_str = request.args.get('data_fim')
    filial_id = request.args.get('filial_id')
    
    hoje = datetime.now().date()
    
    if data_inicio_str:
        data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
    else:
        data_inicio = hoje - timedelta(days=15)
    
    if data_fim_str:
        data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
    else:
        data_fim = hoje + timedelta(days=15)
    
    filial_id = int(filial_id) if filial_id else None
    
    movimentacoes = FluxoCaixaModel.get_movimentacoes(data_inicio, data_fim, filial_id)
    saldo_inicial = FluxoCaixaModel.get_saldo_inicial(data_inicio, filial_id)
    
    resumo = movimentacoes['resumo']
    resumo['saldo_inicial'] = float(saldo_inicial)
    resumo['saldo_final'] = float(saldo_inicial + resumo['saldo_realizado'])
    
    # Converter Decimal para float para JSON
    for key in resumo:
        if isinstance(resumo[key], Decimal):
            resumo[key] = float(resumo[key])
    
    return jsonify(resumo)
