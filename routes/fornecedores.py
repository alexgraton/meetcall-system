"""
Rotas para gerenciamento de Fornecedores
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from functools import wraps
from models.fornecedor import FornecedorModel
from services.cnpj_validator import validar_cnpj, validar_cpf, limpar_documento

fornecedores_bp = Blueprint('fornecedores', __name__, url_prefix='/fornecedores')

# Reusar os decorators já usados no projeto (checar session)
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('Você não tem permissão para acessar esta página.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

@fornecedores_bp.route('/')
@login_required
def lista():
    fornecedores = FornecedorModel.get_all()
    return render_template('fornecedores/lista.html', fornecedores=fornecedores)

@fornecedores_bp.route('/novo', methods=['GET', 'POST'])
@admin_required
def novo():
    if request.method == 'POST':
        # Validar CNPJ/CPF
        cnpj = request.form.get('cnpj', '').strip()
        tipo_pessoa = request.form.get('tipo_pessoa', 'juridica')
        
        if cnpj:
            cnpj_limpo = limpar_documento(cnpj)
            if tipo_pessoa == 'juridica':
                if not validar_cnpj(cnpj_limpo):
                    flash('CNPJ inválido!', 'error')
                    return redirect(url_for('fornecedores.novo'))
            else:  # pessoa fisica
                if not validar_cpf(cnpj_limpo):
                    flash('CPF inválido!', 'error')
                    return redirect(url_for('fornecedores.novo'))
        
        dados = {
            'nome': request.form.get('nome'),
            'razao_social': request.form.get('razao_social'),
            'cnpj': cnpj,
            'tipo_pessoa': tipo_pessoa,
            'email': request.form.get('email'),
            'telefone': request.form.get('telefone'),
            'cep': request.form.get('cep'),
            'endereco': request.form.get('endereco'),
            'numero': request.form.get('numero'),
            'complemento': request.form.get('complemento'),
            'bairro': request.form.get('bairro'),
            'cidade': request.form.get('cidade'),
            'estado': request.form.get('estado'),
            # contatos: será processado via JSON do campo oculto
            'contatos': []
        }
        
        # Processar contatos se enviados via JSON
        import json
        contatos_json = request.form.get('contatos_json', '[]')
        try:
            dados['contatos'] = json.loads(contatos_json)
        except:
            pass
        
        FornecedorModel.create(dados)
        flash('Fornecedor criado com sucesso!', 'success')
        return redirect(url_for('fornecedores.lista'))
    return render_template('fornecedores/form.html')

@fornecedores_bp.route('/editar/<int:fornecedor_id>', methods=['GET', 'POST'])
@admin_required
def editar(fornecedor_id):
    fornecedor = FornecedorModel.get_by_id(fornecedor_id)
    if not fornecedor:
        flash('Fornecedor não encontrado', 'error')
        return redirect(url_for('fornecedores.lista'))
    if request.method == 'POST':
        # Validar CNPJ/CPF
        cnpj = request.form.get('cnpj', '').strip()
        tipo_pessoa = request.form.get('tipo_pessoa', 'juridica')
        
        if cnpj:
            cnpj_limpo = limpar_documento(cnpj)
            if tipo_pessoa == 'juridica':
                if not validar_cnpj(cnpj_limpo):
                    flash('CNPJ inválido!', 'error')
                    return redirect(url_for('fornecedores.editar', fornecedor_id=fornecedor_id))
            else:
                if not validar_cpf(cnpj_limpo):
                    flash('CPF inválido!', 'error')
                    return redirect(url_for('fornecedores.editar', fornecedor_id=fornecedor_id))
        
        dados = {
            'nome': request.form.get('nome'),
            'razao_social': request.form.get('razao_social'),
            'cnpj': cnpj,
            'tipo_pessoa': tipo_pessoa,
            'email': request.form.get('email'),
            'telefone': request.form.get('telefone'),
            'cep': request.form.get('cep'),
            'endereco': request.form.get('endereco'),
            'numero': request.form.get('numero'),
            'complemento': request.form.get('complemento'),
            'bairro': request.form.get('bairro'),
            'cidade': request.form.get('cidade'),
            'estado': request.form.get('estado'),
            'contatos': []
        }
        
        # Processar contatos
        import json
        contatos_json = request.form.get('contatos_json', '[]')
        try:
            dados['contatos'] = json.loads(contatos_json)
        except:
            pass
        
        FornecedorModel.update(fornecedor_id, dados)
        flash('Fornecedor atualizado com sucesso!', 'success')
        return redirect(url_for('fornecedores.lista'))
    return render_template('fornecedores/form.html', fornecedor=fornecedor)

@fornecedores_bp.route('/deletar/<int:fornecedor_id>', methods=['POST'])
@admin_required
def deletar(fornecedor_id):
    try:
        FornecedorModel.delete(fornecedor_id)
        return jsonify({'success': True, 'message': 'Fornecedor desativado'} )
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@fornecedores_bp.route('/toggle-status/<int:fornecedor_id>', methods=['POST'])
@admin_required
def toggle_status(fornecedor_id):
    try:
        FornecedorModel.toggle_status(fornecedor_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
