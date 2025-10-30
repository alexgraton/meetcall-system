"""
Rotas para gerenciamento de Centros de Custo
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from functools import wraps
from models.centro_custo import CentroCustoModel
from models.filial import FilialModel

centro_custos_bp = Blueprint('centro_custos', __name__, url_prefix='/centro-custos')

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
        if session.get('role') != 'admin':
            flash('Acesso negado. Apenas administradores podem acessar esta página.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@centro_custos_bp.route('/')
@login_required
@admin_required
def lista():
    filial_id = request.args.get('filial_id', type=int)
    centros = CentroCustoModel.get_all(filial_id=filial_id)
    filiais = FilialModel.get_all()
    return render_template('centro_custos/lista.html', centros=centros, filiais=filiais, filial_selecionada=filial_id)

@centro_custos_bp.route('/novo', methods=['GET', 'POST'])
@login_required
@admin_required
def novo():
    if request.method == 'POST':
        dados = {
            'descricao': request.form.get('descricao'),
            'filial_id': request.form.get('filial_id') or None,
            'parent_id': request.form.get('parent_id') or None
        }
        
        result = CentroCustoModel.create(dados)
        if result['success']:
            flash(f'Centro de custo {result["codigo"]} cadastrado com sucesso!', 'success')
            return redirect(url_for('centro_custos.lista'))
        else:
            flash(f'Erro ao cadastrar: {result["message"]}', 'error')
    
    filiais = FilialModel.get_all()
    centros = CentroCustoModel.get_all()  # Para seleção de parent
    return render_template('centro_custos/form.html', filiais=filiais, centros=centros)

@centro_custos_bp.route('/editar/<int:centro_custo_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def editar(centro_custo_id):
    centro = CentroCustoModel.get_by_id(centro_custo_id)
    if not centro:
        flash('Centro de custo não encontrado', 'error')
        return redirect(url_for('centro_custos.lista'))
    
    if request.method == 'POST':
        dados = {
            'descricao': request.form.get('descricao'),
            'filial_id': request.form.get('filial_id') or None,
            'parent_id': request.form.get('parent_id') or None
        }
        
        # Validar para não criar ciclo (não pode ser pai de si mesmo)
        if dados.get('parent_id'):
            parent_id = int(dados['parent_id'])
            if parent_id == centro_custo_id:
                flash('Um centro de custo não pode ser pai de si mesmo!', 'error')
                return redirect(url_for('centro_custos.editar', centro_custo_id=centro_custo_id))
        
        CentroCustoModel.update(centro_custo_id, dados)
        flash('Centro de custo atualizado com sucesso!', 'success')
        return redirect(url_for('centro_custos.lista'))
    
    filiais = FilialModel.get_all()
    centros = CentroCustoModel.get_all()  # Para seleção de parent
    # Remover o próprio centro da lista de possíveis pais
    centros = [c for c in centros if c['id'] != centro_custo_id]
    
    return render_template('centro_custos/form.html', centro=centro, filiais=filiais, centros=centros)

@centro_custos_bp.route('/deletar/<int:centro_custo_id>', methods=['POST'])
@login_required
@admin_required
def deletar(centro_custo_id):
    try:
        CentroCustoModel.delete(centro_custo_id)
        return jsonify({'success': True, 'message': 'Centro de custo desativado'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@centro_custos_bp.route('/toggle-status/<int:centro_custo_id>', methods=['POST'])
@login_required
@admin_required
def toggle_status(centro_custo_id):
    try:
        CentroCustoModel.toggle_status(centro_custo_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
