"""
Rotas para gerenciamento de Tipos de Serviços
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from functools import wraps
from models.tipo_servico import TipoServicoModel

# Criar blueprint
tipos_servicos_bp = Blueprint('tipos_servicos', __name__, url_prefix='/tipos-servicos')

# Decorator para exigir autenticação
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login para acessar esta página.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Decorator para exigir permissão de admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login para acessar esta página.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@tipos_servicos_bp.route('/')
@login_required
def lista():
    """Lista todos os tipos de serviços com subtipos"""
    try:
        # Buscar categorias principais (parent_id = NULL)
        categorias = TipoServicoModel.get_all()
        categorias_principais = [c for c in categorias if c.get('parent_id') is None]
        
        # Para cada categoria principal, buscar seus subtipos
        for categoria in categorias_principais:
            categoria['subtipos'] = [c for c in categorias if c.get('parent_id') == categoria['id']]
        
        return render_template('tipos_servicos/lista.html', categorias=categorias_principais)
    except Exception as e:
        flash(f'Erro ao carregar categorias: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@tipos_servicos_bp.route('/novo', methods=['GET', 'POST'])
@login_required
def novo():
    """Cria um novo tipo de serviço"""
    if request.method == 'POST':
        try:
            nome = request.form.get('nome', '').strip()
            descricao = request.form.get('descricao', '').strip() or None
            parent_id = request.form.get('parent_id') or None
            tipo = request.form.get('tipo', 'despesa')
            
            if not nome:
                flash('O nome é obrigatório.', 'error')
                return redirect(url_for('tipos_servicos.novo'))
            
            # Converter parent_id para int se não for None
            if parent_id:
                parent_id = int(parent_id)
            
            tipo_id = TipoServicoModel.create(
                nome=nome,
                descricao=descricao,
                tipo=tipo,
                parent_id=parent_id
            )
            
            flash('Categoria de despesa criada com sucesso!', 'success')
            return redirect(url_for('tipos_servicos.lista'))
            
        except ValueError as e:
            flash(f'Erro de validação: {str(e)}', 'error')
            return redirect(url_for('tipos_servicos.novo'))
        except Exception as e:
            flash(f'Erro ao criar tipo de serviço: {str(e)}', 'error')
            return redirect(url_for('tipos_servicos.novo'))
    
    # GET - mostrar formulário
    categorias = TipoServicoModel.get_categories()
    return render_template('tipos_servicos/form.html', categorias=categorias)

@tipos_servicos_bp.route('/novo-subtipo/<int:categoria_id>', methods=['GET', 'POST'])
@login_required
def novo_subtipo(categoria_id):
    """Cria um novo subtipo dentro de uma categoria"""
    if request.method == 'POST':
        try:
            nome = request.form.get('nome', '').strip()
            descricao = request.form.get('descricao', '').strip()
            
            if not nome:
                flash('O nome é obrigatório.', 'error')
                return redirect(url_for('tipos_servicos.novo_subtipo', categoria_id=categoria_id))
            
            # Buscar categoria pai para pegar o tipo
            categoria = TipoServicoModel.get_by_id(categoria_id)
            if not categoria:
                flash('Categoria não encontrada.', 'error')
                return redirect(url_for('tipos_servicos.lista'))
            
            tipo_id = TipoServicoModel.create(
                nome=nome,
                descricao=descricao,
                tipo=categoria['tipo'],  # Herda o tipo da categoria pai
                parent_id=categoria_id
            )
            
            flash(f'Subtipo "{nome}" criado com sucesso!', 'success')
            return redirect(url_for('tipos_servicos.lista'))
            
        except ValueError as e:
            flash(f'Erro de validação: {str(e)}', 'error')
            return redirect(url_for('tipos_servicos.novo_subtipo', categoria_id=categoria_id))
        except Exception as e:
            flash(f'Erro ao criar subtipo: {str(e)}', 'error')
            return redirect(url_for('tipos_servicos.novo_subtipo', categoria_id=categoria_id))
    
    # GET - mostrar formulário
    categoria = TipoServicoModel.get_by_id(categoria_id)
    if not categoria:
        flash('Categoria não encontrada.', 'error')
        return redirect(url_for('tipos_servicos.lista'))
    
    return render_template('tipos_servicos/form_subtipo.html', categoria=categoria)


@tipos_servicos_bp.route('/editar/<int:tipo_id>', methods=['GET', 'POST'])
@login_required
def editar(tipo_id):
    """Edita um tipo de serviço existente"""
    tipo = TipoServicoModel.get_by_id(tipo_id)
    
    if not tipo:
        flash('Tipo de serviço não encontrado.', 'error')
        return redirect(url_for('tipos_servicos.lista'))
    
    if request.method == 'POST':
        try:
            nome = request.form.get('nome', '').strip()
            descricao = request.form.get('descricao', '').strip() or None
            parent_id = request.form.get('parent_id') or None
            
            if not nome:
                flash('O nome é obrigatório.', 'error')
                return redirect(url_for('tipos_servicos.editar', tipo_id=tipo_id))
            
            # Converter parent_id para int se não for None
            if parent_id:
                parent_id = int(parent_id)
            
            TipoServicoModel.update(
                tipo_id=tipo_id,
                nome=nome,
                descricao=descricao,
                parent_id=parent_id
            )
            
            flash('Categoria de despesa atualizada com sucesso!', 'success')
            return redirect(url_for('tipos_servicos.lista'))
            
        except ValueError as e:
            flash(f'Erro de validação: {str(e)}', 'error')
            return redirect(url_for('tipos_servicos.editar', tipo_id=tipo_id))
        except Exception as e:
            flash(f'Erro ao atualizar categoria: {str(e)}', 'error')
            return redirect(url_for('tipos_servicos.editar', tipo_id=tipo_id))
    
    # GET - mostrar formulário
    categorias = TipoServicoModel.get_categories()
    return render_template('tipos_servicos/form.html', tipo=tipo, categorias=categorias)

@tipos_servicos_bp.route('/excluir/<int:tipo_id>')
@login_required
def excluir(tipo_id):
    """Exclui um tipo de serviço (GET para simplificar)"""
    try:
        # Buscar o tipo para verificar se tem filhos
        tipo = TipoServicoModel.get_by_id(tipo_id)
        if not tipo:
            flash('Categoria não encontrada.', 'error')
            return redirect(url_for('tipos_servicos.lista'))
        
        # Verificar se tem filhos (subtipos)
        categorias = TipoServicoModel.get_all()
        filhos = [c for c in categorias if c.get('parent_id') == tipo_id]
        
        if filhos:
            flash(f'Não é possível excluir "{tipo["nome"]}" porque possui {len(filhos)} subtipo(s). Exclua os subtipos primeiro.', 'error')
            return redirect(url_for('tipos_servicos.lista'))
        
        # Excluir
        TipoServicoModel.delete(tipo_id)
        flash(f'Categoria "{tipo["nome"]}" excluída com sucesso!', 'success')
        return redirect(url_for('tipos_servicos.lista'))
        
    except Exception as e:
        flash(f'Erro ao excluir: {str(e)}', 'error')
        return redirect(url_for('tipos_servicos.lista'))

@tipos_servicos_bp.route('/deletar/<int:tipo_id>', methods=['POST'])
@login_required
def deletar(tipo_id):
    """Exclui logicamente um tipo de serviço"""
    try:
        # Verificar se tem filhos
        if TipoServicoModel.has_children(tipo_id):
            return jsonify({
                'success': False,
                'message': 'Este tipo possui subcategorias. Todas serão desativadas também.'
            })
        
        TipoServicoModel.delete(tipo_id)
        return jsonify({
            'success': True,
            'message': 'Tipo de serviço excluído com sucesso!'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao excluir tipo de serviço: {str(e)}'
        }), 500

@tipos_servicos_bp.route('/toggle-status/<int:tipo_id>', methods=['POST'])
@login_required
def toggle_status(tipo_id):
    """Alterna o status ativo/inativo de um tipo de serviço"""
    try:
        TipoServicoModel.toggle_status(tipo_id)
        return jsonify({
            'success': True,
            'message': 'Status alterado com sucesso!'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao alterar status: {str(e)}'
        }), 500
