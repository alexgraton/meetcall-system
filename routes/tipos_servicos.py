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
        if session.get('role') != 'admin':
            flash('Você não tem permissão para acessar esta página.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@tipos_servicos_bp.route('/')
@login_required
def lista():
    """Lista todos os tipos de serviços"""
    try:
        tipos = TipoServicoModel.get_hierarchy()
        return render_template('tipos_servicos/lista.html', tipos=tipos)
    except Exception as e:
        flash(f'Erro ao carregar tipos de serviços: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@tipos_servicos_bp.route('/novo', methods=['GET', 'POST'])
@admin_required
def novo():
    """Cria um novo tipo de serviço"""
    if request.method == 'POST':
        try:
            nome = request.form.get('nome', '').strip()
            descricao = request.form.get('descricao', '').strip() or None
            parent_id = request.form.get('parent_id') or None
            tipo = request.form.get('tipo', 'despesa')
            aliquota = float(request.form.get('aliquota', 0))
            margem_esperada = float(request.form.get('margem_esperada', 0))
            
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
                parent_id=parent_id,
                aliquota=aliquota,
                margem_esperada=margem_esperada
            )
            
            flash('Tipo de serviço criado com sucesso!', 'success')
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

@tipos_servicos_bp.route('/editar/<int:tipo_id>', methods=['GET', 'POST'])
@admin_required
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
            aliquota = float(request.form.get('aliquota', 0))
            margem_esperada = float(request.form.get('margem_esperada', 0))
            
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
                parent_id=parent_id,
                aliquota=aliquota,
                margem_esperada=margem_esperada
            )
            
            flash('Tipo de serviço atualizado com sucesso!', 'success')
            return redirect(url_for('tipos_servicos.lista'))
            
        except ValueError as e:
            flash(f'Erro de validação: {str(e)}', 'error')
            return redirect(url_for('tipos_servicos.editar', tipo_id=tipo_id))
        except Exception as e:
            flash(f'Erro ao atualizar tipo de serviço: {str(e)}', 'error')
            return redirect(url_for('tipos_servicos.editar', tipo_id=tipo_id))
    
    # GET - mostrar formulário
    categorias = TipoServicoModel.get_categories()
    return render_template('tipos_servicos/form.html', tipo=tipo, categorias=categorias)

@tipos_servicos_bp.route('/deletar/<int:tipo_id>', methods=['POST'])
@admin_required
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
@admin_required
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
