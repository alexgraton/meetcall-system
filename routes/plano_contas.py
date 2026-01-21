"""
Rotas para gerenciamento do Plano de Contas
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from functools import wraps
from models.plano_conta import PlanoContaModel
from utils.auditoria import auditar_agora

plano_contas_bp = Blueprint('plano_contas', __name__, url_prefix='/plano-contas')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@plano_contas_bp.route('/')
@login_required
@login_required
def lista():
    tipo_filtro = request.args.get('tipo')
    nivel_filtro = request.args.get('nivel', type=int)
    
    # Modo de visualização: lista ou hierarquia
    modo = request.args.get('modo', 'hierarquia')
    
    if modo == 'hierarquia':
        contas = PlanoContaModel.get_hierarchy(tipo=tipo_filtro)
    else:
        contas = PlanoContaModel.get_all(tipo=tipo_filtro, nivel=nivel_filtro)
    
    return render_template('plano_contas/lista.html', contas=contas, modo=modo, tipo_filtro=tipo_filtro, nivel_filtro=nivel_filtro)

@plano_contas_bp.route('/novo', methods=['GET', 'POST'])
@login_required
@login_required
def novo():
    if request.method == 'POST':
        dados = {
            'codigo': request.form.get('codigo'),
            'descricao': request.form.get('descricao'),
            'tipo': request.form.get('tipo'),
            'dre_grupo': request.form.get('dre_grupo') or None,
            'ordem': request.form.get('ordem', 0)
        }
        
        # Validar formato do código (ex: 1.1.01.001)
        codigo = dados['codigo']
        if not codigo or not all(c.isdigit() or c == '.' for c in codigo):
            flash('Código inválido! Use o formato: 1.1.01.001', 'error')
            return redirect(url_for('plano_contas.novo'))
        
        result = PlanoContaModel.create(dados)
        if result['success']:
            # Auditoria
            auditar_agora('plano_contas', result.get('id', 0), 'insert', dados)
            
            flash(f'Conta {result["codigo"]} cadastrada com sucesso!', 'success')
            return redirect(url_for('plano_contas.lista'))
        else:
            flash(f'Erro ao cadastrar: {result["message"]}', 'error')
    
    return render_template('plano_contas/form.html')

@plano_contas_bp.route('/editar/<int:conta_id>', methods=['GET', 'POST'])
@login_required
@login_required
def editar(conta_id):
    conta = PlanoContaModel.get_by_id(conta_id)
    if not conta:
        flash('Conta não encontrada', 'error')
        return redirect(url_for('plano_contas.lista'))
    
    if request.method == 'POST':
        dados = {
            'descricao': request.form.get('descricao'),
            'dre_grupo': request.form.get('dre_grupo') or None,
            'ordem': request.form.get('ordem', 0)
        }
        
        PlanoContaModel.update(conta_id, dados)
        
        # Auditoria
        auditar_agora('plano_contas', conta_id, 'update', dados)
        
        flash('Conta atualizada com sucesso!', 'success')
        return redirect(url_for('plano_contas.lista'))
    
    return render_template('plano_contas/form.html', conta=conta)

@plano_contas_bp.route('/deletar/<int:conta_id>', methods=['POST'])
@login_required
@login_required
def deletar(conta_id):
    try:
        result = PlanoContaModel.delete(conta_id)
        
        if result.get('success'):
            # Auditoria
            auditar_agora('plano_contas', conta_id, 'delete')
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@plano_contas_bp.route('/toggle-status/<int:conta_id>', methods=['POST'])
@login_required
@login_required
def toggle_status(conta_id):
    try:
        PlanoContaModel.toggle_status(conta_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@plano_contas_bp.route('/api/analiticas')
@login_required
def api_analiticas():
    """API para retornar apenas contas analíticas (para uso em selects)"""
    tipo = request.args.get('tipo')
    contas = PlanoContaModel.get_analiticas(tipo=tipo)
    return jsonify([{'id': c['id'], 'codigo': c['codigo'], 'descricao': c['descricao']} for c in contas])
