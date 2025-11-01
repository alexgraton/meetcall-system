"""
Rotas para Dashboard Financeiro
"""

from flask import Blueprint, render_template, jsonify, request, session, redirect, url_for
from functools import wraps
from models.dashboard import DashboardModel
from decimal import Decimal

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@dashboard_bp.route('/')
@login_required
def index():
    """Página principal do dashboard"""
    try:
        # Buscar dados do dashboard
        kpis = DashboardModel.get_kpis_gerais()
        inadimplencia = DashboardModel.get_inadimplencia()
        evolucao = DashboardModel.get_evolucao_mensal(meses=6)
        top_clientes = DashboardModel.get_top_clientes(limite=5)
        top_fornecedores = DashboardModel.get_top_fornecedores(limite=5)
        distribuicao = DashboardModel.get_distribuicao_despesas()
        
        return render_template(
            'dashboard/index.html',
            kpis=kpis,
            inadimplencia=inadimplencia,
            evolucao=evolucao,
            top_clientes=top_clientes,
            top_fornecedores=top_fornecedores,
            distribuicao=distribuicao
        )
    except Exception as e:
        print(f"Erro ao carregar dashboard: {str(e)}")
        return render_template('dashboard/index.html', erro=str(e))

@dashboard_bp.route('/api/kpis')
@login_required
def api_kpis():
    """API para buscar KPIs gerais"""
    try:
        kpis = DashboardModel.get_kpis_gerais()
        
        # Converter Decimal para float
        def converter_decimal(obj):
            if isinstance(obj, dict):
                return {k: converter_decimal(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [converter_decimal(item) for item in obj]
            elif isinstance(obj, Decimal):
                return float(obj)
            return obj
        
        return jsonify(converter_decimal(kpis))
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@dashboard_bp.route('/api/evolucao')
@login_required
def api_evolucao():
    """API para buscar evolução mensal"""
    try:
        meses = request.args.get('meses', 6, type=int)
        evolucao = DashboardModel.get_evolucao_mensal(meses=meses)
        
        # Converter para formato JSON
        dados = {
            'labels': [item['mes'] for item in evolucao],
            'receitas': [float(item['receitas']) for item in evolucao],
            'despesas': [float(item['despesas']) for item in evolucao],
            'saldos': [float(item['saldo']) for item in evolucao]
        }
        
        return jsonify(dados)
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@dashboard_bp.route('/api/inadimplencia')
@login_required
def api_inadimplencia():
    """API para buscar dados de inadimplência"""
    try:
        inadimplencia = DashboardModel.get_inadimplencia()
        
        dados = {
            'quantidade_vencidas': inadimplencia['quantidade_vencidas'],
            'valor_vencido': float(inadimplencia['valor_vencido']),
            'valor_total': float(inadimplencia['valor_total']),
            'taxa_inadimplencia': float(inadimplencia['taxa_inadimplencia'])
        }
        
        return jsonify(dados)
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@dashboard_bp.route('/api/top-clientes')
@login_required
def api_top_clientes():
    """API para buscar top clientes"""
    try:
        limite = request.args.get('limite', 5, type=int)
        clientes = DashboardModel.get_top_clientes(limite=limite)
        
        # Converter Decimal
        for cliente in clientes:
            cliente['valor_total'] = float(cliente['valor_total'])
        
        return jsonify(clientes)
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@dashboard_bp.route('/api/top-fornecedores')
@login_required
def api_top_fornecedores():
    """API para buscar top fornecedores"""
    try:
        limite = request.args.get('limite', 5, type=int)
        fornecedores = DashboardModel.get_top_fornecedores(limite=limite)
        
        # Converter Decimal
        for fornecedor in fornecedores:
            fornecedor['valor_total'] = float(fornecedor['valor_total'])
        
        return jsonify(fornecedores)
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@dashboard_bp.route('/api/distribuicao-despesas')
@login_required
def api_distribuicao_despesas():
    """API para buscar distribuição de despesas"""
    try:
        distribuicao = DashboardModel.get_distribuicao_despesas()
        
        dados = {
            'labels': [f"{item['codigo']} - {item['descricao']}" for item in distribuicao],
            'valores': [float(item['valor']) for item in distribuicao]
        }
        
        return jsonify(dados)
    except Exception as e:
        return jsonify({'erro': str(e)}), 500
