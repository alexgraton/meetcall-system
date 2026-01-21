"""
Rotas para gerenciamento de Filiais
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from models.filial import FilialModel
from services.cnpj_validator import validar_cnpj, formatar_cnpj, limpar_documento

filiais_bp = Blueprint('filiais', __name__, url_prefix='/filiais')

def login_required(f):
    """Decorator para verificar se usuário está logado"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@filiais_bp.route('/')
@login_required
def lista():
    """Lista todas as filiais"""
    try:
        filiais = FilialModel.get_all()
        return render_template('filiais/lista.html', filiais=filiais)
    except Exception as e:
        flash(f'Erro ao carregar filiais: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@filiais_bp.route('/nova', methods=['GET', 'POST'])
@login_required
def nova():
    """Cria uma nova filial"""
    if request.method == 'POST':
        try:
            # Coleta dados do formulário
            data = {
                'codigo': request.form.get('codigo', '').strip(),
                'nome': request.form.get('nome', '').strip(),
                'razao_social': request.form.get('razao_social', '').strip(),
                'cnpj': request.form.get('cnpj', '').strip(),
                'email': request.form.get('email', '').strip(),
                'telefone': request.form.get('telefone', '').strip(),
                'cep': request.form.get('cep', '').strip(),
                'endereco': request.form.get('endereco', '').strip(),
                'numero': request.form.get('numero', '').strip(),
                'complemento': request.form.get('complemento', '').strip(),
                'bairro': request.form.get('bairro', '').strip(),
                'cidade': request.form.get('cidade', '').strip(),
                'estado': request.form.get('estado', '').strip(),
                'is_matriz': request.form.get('is_matriz') == 'on'
            }
            
            # Validações
            if not data['codigo'] or not data['nome']:
                flash('Código e Nome são obrigatórios!', 'error')
                return render_template('filiais/form.html', filial=data)
            
            # Valida CNPJ se fornecido
            if data['cnpj']:
                cnpj_limpo = limpar_documento(data['cnpj'])
                if not validar_cnpj(cnpj_limpo):
                    flash('CNPJ inválido!', 'error')
                    return render_template('filiais/form.html', filial=data)
                data['cnpj'] = formatar_cnpj(cnpj_limpo)
            
            # Cria a filial
            filial_id = FilialModel.create(data, session['user_id'])
            flash(f'Filial {data["nome"]} criada com sucesso!', 'success')
            return redirect(url_for('filiais.lista'))
            
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('filiais/form.html', filial=data)
        except Exception as e:
            flash(f'Erro ao criar filial: {str(e)}', 'error')
            return render_template('filiais/form.html', filial=data)
    
    return render_template('filiais/form.html', filial=None)

@filiais_bp.route('/editar/<int:filial_id>', methods=['GET', 'POST'])
@login_required
def editar(filial_id):
    """Edita uma filial existente"""
    if request.method == 'POST':
        try:
            # Coleta dados do formulário
            data = {
                'codigo': request.form.get('codigo', '').strip(),
                'nome': request.form.get('nome', '').strip(),
                'razao_social': request.form.get('razao_social', '').strip(),
                'cnpj': request.form.get('cnpj', '').strip(),
                'email': request.form.get('email', '').strip(),
                'telefone': request.form.get('telefone', '').strip(),
                'cep': request.form.get('cep', '').strip(),
                'endereco': request.form.get('endereco', '').strip(),
                'numero': request.form.get('numero', '').strip(),
                'complemento': request.form.get('complemento', '').strip(),
                'bairro': request.form.get('bairro', '').strip(),
                'cidade': request.form.get('cidade', '').strip(),
                'estado': request.form.get('estado', '').strip(),
                'is_matriz': request.form.get('is_matriz') == 'on'
            }
            
            # Validações
            if not data['codigo'] or not data['nome']:
                flash('Código e Nome são obrigatórios!', 'error')
                return render_template('filiais/form.html', filial=data, filial_id=filial_id)
            
            # Valida CNPJ se fornecido
            if data['cnpj']:
                cnpj_limpo = limpar_documento(data['cnpj'])
                if not validar_cnpj(cnpj_limpo):
                    flash('CNPJ inválido!', 'error')
                    return render_template('filiais/form.html', filial=data, filial_id=filial_id)
                data['cnpj'] = formatar_cnpj(cnpj_limpo)
            
            # Atualiza a filial
            if FilialModel.update(filial_id, data):
                flash('Filial atualizada com sucesso!', 'success')
                return redirect(url_for('filiais.lista'))
            else:
                flash('Nenhuma alteração foi realizada.', 'warning')
                return redirect(url_for('filiais.lista'))
            
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('filiais/form.html', filial=data, filial_id=filial_id)
        except Exception as e:
            flash(f'Erro ao atualizar filial: {str(e)}', 'error')
            return render_template('filiais/form.html', filial=data, filial_id=filial_id)
    
    # GET - Carrega dados da filial
    filial = FilialModel.get_by_id(filial_id)
    if not filial:
        flash('Filial não encontrada!', 'error')
        return redirect(url_for('filiais.lista'))
    
    return render_template('filiais/form.html', filial=filial, filial_id=filial_id)

@filiais_bp.route('/toggle/<int:filial_id>', methods=['POST'])
@login_required
def toggle(filial_id):
    """Ativa ou desativa uma filial"""
    try:
        if FilialModel.toggle_status(filial_id):
            flash('Status da filial alterado com sucesso!', 'success')
        else:
            flash('Erro ao alterar status da filial.', 'error')
    except Exception as e:
        flash(f'Erro: {str(e)}', 'error')
    
    return redirect(url_for('filiais.lista'))

@filiais_bp.route('/deletar/<int:filial_id>', methods=['POST'])
@login_required
def deletar(filial_id):
    """Deleta (desativa) uma filial"""
    try:
        if FilialModel.delete(filial_id):
            flash('Filial removida com sucesso!', 'success')
        else:
            flash('Erro ao remover filial.', 'error')
    except Exception as e:
        flash(f'Erro: {str(e)}', 'error')
    
    return redirect(url_for('filiais.lista'))

@filiais_bp.route('/validar-cnpj', methods=['POST'])
def validar_cnpj_ajax():
    """Valida CNPJ via AJAX"""
    cnpj = request.json.get('cnpj', '')
    cnpj_limpo = limpar_documento(cnpj)
    
    if validar_cnpj(cnpj_limpo):
        return jsonify({
            'valido': True,
            'cnpj_formatado': formatar_cnpj(cnpj_limpo)
        })
    else:
        return jsonify({'valido': False})
