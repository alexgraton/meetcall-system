"""
Routes para gerenciamento de Capacity (operadores por cliente/produto)
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from models.capacity import CapacityModel
from datetime import datetime

capacity_bp = Blueprint('capacity', __name__, url_prefix='/capacity')
capacity_model = CapacityModel()

@capacity_bp.route('/')
def index():
    """Tela principal de gerenciamento de capacity"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    clientes = capacity_model.get_clientes_com_produtos()
    
    return render_template('capacity/index.html', clientes=clientes)

@capacity_bp.route('/api/salvar', methods=['POST'])
def api_salvar():
    """API para salvar capacity"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    try:
        data = request.get_json()
        
        cliente_id = data.get('cliente_id')
        produto_id = data.get('produto_id')  # Pode ser None
        capacity_atual = int(data.get('capacity_atual', 0))
        capacity_necessario = int(data.get('capacity_necessario', 0))
        data_vigencia = data.get('data_vigencia')
        observacoes = data.get('observacoes')
        
        if not cliente_id or not data_vigencia:
            return jsonify({'success': False, 'message': 'Cliente e data de vigência são obrigatórios'}), 400
        
        # Valida formato da data
        try:
            datetime.strptime(data_vigencia, '%Y-%m-%d')
        except ValueError:
            return jsonify({'success': False, 'message': 'Data inválida'}), 400
        
        capacity_id = capacity_model.salvar_capacity(
            cliente_id=cliente_id,
            produto_id=produto_id,
            capacity_atual=capacity_atual,
            capacity_necessario=capacity_necessario,
            data_vigencia=data_vigencia,
            usuario_id=session['user_id'],
            observacoes=observacoes
        )
        
        return jsonify({
            'success': True, 
            'message': 'Capacity salvo com sucesso',
            'id': capacity_id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao salvar: {str(e)}'}), 500

@capacity_bp.route('/api/historico/<int:cliente_id>')
def api_historico_cliente(cliente_id):
    """API para buscar histórico de capacity de um cliente"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    try:
        produto_id = request.args.get('produto_id', type=int)
        limit = request.args.get('limit', 10, type=int)
        
        historico = capacity_model.get_historico(
            cliente_id=cliente_id,
            produto_id=produto_id,
            limit=limit
        )
        
        # Formata datas para JSON
        for item in historico:
            if item.get('data_vigencia'):
                item['data_vigencia'] = item['data_vigencia'].strftime('%Y-%m-%d')
            if item.get('data_alteracao'):
                item['data_alteracao'] = item['data_alteracao'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({'success': True, 'historico': historico})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao buscar histórico: {str(e)}'}), 500

@capacity_bp.route('/api/atual')
def api_capacity_atual():
    """API para buscar capacity atual (mais recente)"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    try:
        cliente_id = request.args.get('cliente_id', type=int)
        produto_id = request.args.get('produto_id', type=int)
        data_referencia = request.args.get('data_referencia')  # Formato: YYYY-MM-DD
        
        capacities = capacity_model.get_capacity_atual(
            cliente_id=cliente_id,
            produto_id=produto_id,
            data_referencia=data_referencia
        )
        
        # Formata datas para JSON
        for item in capacities:
            if item.get('data_vigencia'):
                item['data_vigencia'] = item['data_vigencia'].strftime('%Y-%m-%d')
            if item.get('data_alteracao'):
                item['data_alteracao'] = item['data_alteracao'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({'success': True, 'capacities': capacities})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao buscar capacity: {str(e)}'}), 500

@capacity_bp.route('/api/total-periodo')
def api_total_periodo():
    """API para buscar total de capacity por período"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    try:
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        if not data_inicio or not data_fim:
            return jsonify({'success': False, 'message': 'Data início e fim são obrigatórias'}), 400
        
        totais = capacity_model.get_total_capacity_por_periodo(data_inicio, data_fim)
        
        # Converte Decimal para float para JSON
        for item in totais:
            if item.get('capacity_medio'):
                item['capacity_medio'] = float(item['capacity_medio'])
        
        return jsonify({'success': True, 'totais': totais})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao buscar totais: {str(e)}'}), 500
