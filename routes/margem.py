"""
Routes para Análise de Margem Operacional
Controla competências, rateio de receitas/despesas e dashboard
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from models.margem_operacional import MargemOperacionalModel
from models.capacity import CapacityModel
from decimal import Decimal
import json

margem_bp = Blueprint('margem', __name__, url_prefix='/margem')
margem_model = MargemOperacionalModel()
capacity_model = CapacityModel()

@margem_bp.route('/')
def index():
    """Tela principal - seleção de competência"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    competencias = margem_model.get_competencias()
    
    return render_template('margem/index.html', competencias=competencias)

@margem_bp.route('/competencia/<int:competencia_id>')
def competencia_detalhe(competencia_id):
    """Detalhes de uma competência - menu de ações"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    competencia = margem_model.get_competencia(competencia_id)
    
    if not competencia:
        return redirect(url_for('margem.index'))
    
    # Busca status do rateio
    status = margem_model.get_status_rateio_competencia(competencia_id)
    
    return render_template('margem/competencia.html', 
                         competencia=competencia, 
                         status=status)

@margem_bp.route('/receitas/<int:competencia_id>')
def receitas(competencia_id):
    """Tela de rateio de receitas"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    competencia = margem_model.get_competencia(competencia_id)
    
    if not competencia or competencia['status'] == 'fechada':
        return redirect(url_for('margem.index'))
    
    receitas = margem_model.get_receitas_competencia(competencia['competencia'])
    
    # Para cada receita, busca rateios existentes
    for receita in receitas:
        receita['rateios'] = margem_model.get_rateios_receita(
            receita['id'], 
            competencia_id
        )
    
    return render_template('margem/receitas.html', 
                         competencia=competencia, 
                         receitas=receitas)

@margem_bp.route('/despesas/<int:competencia_id>')
def despesas(competencia_id):
    """Tela de rateio de despesas"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    competencia = margem_model.get_competencia(competencia_id)
    
    if not competencia or competencia['status'] == 'fechada':
        return redirect(url_for('margem.index'))
    
    despesas = margem_model.get_despesas_competencia(competencia['competencia'])
    
    # Para cada despesa, busca rateios existentes
    for despesa in despesas:
        despesa['rateios'] = margem_model.get_rateios_despesa(
            despesa['id'], 
            competencia_id
        )
    
    # Busca clientes com produtos para interface
    clientes = capacity_model.get_clientes_com_produtos()
    
    return render_template('margem/despesas.html', 
                         competencia=competencia, 
                         despesas=despesas,
                         clientes=clientes)

@margem_bp.route('/dashboard/<int:competencia_id>')
def dashboard(competencia_id):
    """Dashboard de margem operacional"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    competencia = margem_model.get_competencia(competencia_id)
    
    if not competencia:
        return redirect(url_for('margem.index'))
    
    # Busca resumo de margem
    resumo = margem_model.get_resumo_margem(competencia=competencia['competencia'])
    
    # Agrupa por cliente/produto
    dados = {}
    for item in resumo:
        key = f"{item['cliente_id']}_{item['produto_id'] if item['produto_id'] else '0'}"
        if key not in dados:
            dados[key] = {
                'cliente_nome': item['cliente_nome'],
                'produto_nome': item['produto_nome'],
                'total_receitas': 0,
                'total_despesas': 0,
                'lucro': 0,
                'margem_percentual': 0
            }
        
        dados[key]['total_receitas'] += float(item['total_receitas'] or 0)
        dados[key]['total_despesas'] += float(item['total_despesas'] or 0)
        dados[key]['lucro'] = dados[key]['total_receitas'] - dados[key]['total_despesas']
        
        if dados[key]['total_receitas'] > 0:
            dados[key]['margem_percentual'] = round(
                (dados[key]['lucro'] / dados[key]['total_receitas']) * 100, 2
            )
    
    return render_template('margem/dashboard.html', 
                         competencia=competencia, 
                         dados=list(dados.values()))

@margem_bp.route('/dashboard/anual/<int:ano>')
def dashboard_anual(ano):
    """Dashboard anual comparativo"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    resumo = margem_model.get_resumo_margem(ano=ano)
    
    # Organiza dados por cliente/produto e mês
    dados = {}
    for item in resumo:
        key = f"{item['cliente_id']}_{item['produto_id'] if item['produto_id'] else '0'}"
        if key not in dados:
            dados[key] = {
                'cliente_nome': item['cliente_nome'],
                'produto_nome': item['produto_nome'],
                'meses': {}
            }
        
        mes = item['competencia'].split('/')[0]
        dados[key]['meses'][mes] = {
            'receitas': float(item['total_receitas'] or 0),
            'despesas': float(item['total_despesas'] or 0),
            'lucro': float(item['lucro'] or 0),
            'margem': float(item['margem_percentual'] or 0)
        }
    
    return render_template('margem/dashboard_anual.html', 
                         ano=ano, 
                         dados=list(dados.values()))

# ========== APIs ==========

@margem_bp.route('/api/competencia/criar', methods=['POST'])
def api_criar_competencia():
    """API para criar nova competência"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    try:
        data = request.get_json()
        competencia = data.get('competencia')  # Formato: MM/YYYY
        
        if not competencia:
            return jsonify({'success': False, 'message': 'Competência é obrigatória'}), 400
        
        # Valida formato
        try:
            mes, ano = competencia.split('/')
            if len(mes) != 2 or len(ano) != 4:
                raise ValueError()
            int(mes), int(ano)
        except:
            return jsonify({'success': False, 'message': 'Formato inválido. Use MM/YYYY'}), 400
        
        competencia_id = margem_model.criar_competencia(competencia, session['user_id'])
        
        return jsonify({
            'success': True,
            'message': 'Competência criada com sucesso',
            'id': competencia_id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'}), 500

@margem_bp.route('/api/competencia/<int:competencia_id>/fechar', methods=['POST'])
def api_fechar_competencia(competencia_id):
    """API para fechar competência"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    try:
        if margem_model.fechar_competencia(competencia_id, session['user_id']):
            return jsonify({'success': True, 'message': 'Competência fechada com sucesso'})
        else:
            return jsonify({'success': False, 'message': 'Erro ao fechar competência'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'}), 500

@margem_bp.route('/api/competencia/<int:competencia_id>/reabrir', methods=['POST'])
def api_reabrir_competencia(competencia_id):
    """API para reabrir competência"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    try:
        if margem_model.reabrir_competencia(competencia_id):
            return jsonify({'success': True, 'message': 'Competência reaberta com sucesso'})
        else:
            return jsonify({'success': False, 'message': 'Erro ao reabrir competência'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'}), 500

@margem_bp.route('/api/receita/ratear', methods=['POST'])
def api_ratear_receita():
    """API para ratear receita entre produtos"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    try:
        data = request.get_json()
        
        competencia_id = data.get('competencia_id')
        conta_receber_id = data.get('conta_receber_id')
        rateios = data.get('rateios', [])  # Lista de {cliente_id, produto_id, percentual, valor}
        
        if not competencia_id or not conta_receber_id or not rateios:
            return jsonify({'success': False, 'message': 'Dados incompletos'}), 400
        
        # Valida soma de percentuais
        total_percentual = sum(float(r.get('percentual', 0)) for r in rateios)
        if abs(total_percentual - 100.0) > 0.01:
            return jsonify({'success': False, 'message': f'Soma dos percentuais deve ser 100%. Atual: {total_percentual}%'}), 400
        
        # Limpa rateios anteriores
        margem_model.limpar_rateios_receita(conta_receber_id, competencia_id)
        
        # Salva novos rateios
        for rateio in rateios:
            margem_model.salvar_rateio_receita(
                competencia_id=competencia_id,
                conta_receber_id=conta_receber_id,
                cliente_id=rateio['cliente_id'],
                produto_id=rateio.get('produto_id'),
                percentual=float(rateio['percentual']),
                valor_rateado=float(rateio['valor']),
                usuario_id=session['user_id']
            )
        
        return jsonify({'success': True, 'message': 'Receita rateada com sucesso'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'}), 500

@margem_bp.route('/api/despesa/ratear', methods=['POST'])
def api_ratear_despesa():
    """API para ratear despesa entre clientes/produtos"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    try:
        data = request.get_json()
        
        competencia_id = data.get('competencia_id')
        conta_pagar_id = data.get('conta_pagar_id')
        tipo_rateio = data.get('tipo_rateio')  # 'percentual', 'valor_fixo', 'capacity'
        rateios = data.get('rateios', [])
        valor_total_despesa = float(data.get('valor_total', 0))
        
        if not competencia_id or not conta_pagar_id or not tipo_rateio:
            return jsonify({'success': False, 'message': 'Dados incompletos'}), 400
        
        # Limpa rateios anteriores
        margem_model.limpar_rateios_despesa(conta_pagar_id, competencia_id)
        
        # Se tipo capacity, aplica rateio automático
        if tipo_rateio == 'capacity':
            competencia = margem_model.get_competencia(competencia_id)
            sucesso = margem_model.aplicar_rateio_automatico_capacity(
                competencia_id=competencia_id,
                conta_pagar_id=conta_pagar_id,
                valor_total=valor_total_despesa,
                competencia=competencia['competencia'],
                usuario_id=session['user_id']
            )
            
            if sucesso:
                return jsonify({'success': True, 'message': 'Despesa rateada automaticamente por capacity'})
            else:
                return jsonify({'success': False, 'message': 'Nenhum capacity cadastrado para esta competência'}), 400
        
        # Rateio manual (percentual ou valor_fixo)
        if not rateios:
            return jsonify({'success': False, 'message': 'Rateios não informados'}), 400
        
        # Valida soma dos valores
        total_rateado = sum(float(r.get('valor', 0)) for r in rateios)
        if total_rateado > valor_total_despesa:
            return jsonify({'success': False, 'message': f'Soma dos rateios (R$ {total_rateado:.2f}) excede valor da despesa (R$ {valor_total_despesa:.2f})'}), 400
        
        # Salva rateios
        for rateio in rateios:
            percentual = None
            if tipo_rateio == 'percentual':
                percentual = float(rateio.get('percentual', 0))
            
            margem_model.salvar_rateio_despesa(
                competencia_id=competencia_id,
                conta_pagar_id=conta_pagar_id,
                cliente_id=rateio['cliente_id'],
                produto_id=rateio.get('produto_id'),
                tipo_rateio=tipo_rateio,
                percentual=percentual,
                valor_rateado=float(rateio['valor']),
                usuario_id=session['user_id'],
                observacoes=rateio.get('observacoes')
            )
        
        return jsonify({'success': True, 'message': 'Despesa rateada com sucesso'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'}), 500

@margem_bp.route('/api/dashboard/detalhamento/<int:competencia_id>')
def api_detalhamento_despesas(competencia_id):
    """API para buscar detalhamento de despesas por tipo de serviço"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'}), 401
    
    try:
        cliente_id = request.args.get('cliente_id', type=int)
        produto_id = request.args.get('produto_id', type=int)
        
        detalhamento = margem_model.get_detalhamento_despesas(
            competencia_id=competencia_id,
            cliente_id=cliente_id,
            produto_id=produto_id
        )
        
        # Converte Decimal para float
        for item in detalhamento:
            if item.get('total'):
                item['total'] = float(item['total'])
        
        return jsonify({'success': True, 'detalhamento': detalhamento})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro: {str(e)}'}), 500
