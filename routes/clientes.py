"""
Rotas para gerenciamento de Clientes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from functools import wraps
from models.cliente import ClienteModel
from services.cnpj_validator import validar_cnpj, validar_cpf, limpar_documento
import json

clientes_bp = Blueprint('clientes', __name__, url_prefix='/clientes')

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

@clientes_bp.route('/')
@login_required
def lista():
    clientes = ClienteModel.get_all()
    return render_template('clientes/lista.html', clientes=clientes)

@clientes_bp.route('/novo', methods=['GET', 'POST'])
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
                    return redirect(url_for('clientes.novo'))
            else:
                if not validar_cpf(cnpj_limpo):
                    flash('CPF inválido!', 'error')
                    return redirect(url_for('clientes.novo'))
        
        dados = {
            'nome': request.form.get('nome'),
            'razao_social': request.form.get('razao_social'),
            'cnpj': cnpj,
            'tipo_pessoa': tipo_pessoa,
            'email': request.form.get('email'),
            'telefone': request.form.get('telefone'),
            'cep': request.form.get('cep'),
            'logradouro': request.form.get('logradouro'),  # Form field name
            'numero': request.form.get('numero'),
            'complemento': request.form.get('complemento'),
            'bairro': request.form.get('bairro'),
            'cidade': request.form.get('cidade'),
            'uf': request.form.get('uf'),  # Form field name
            'contatos': [],
            'produtos': []
        }
        
        # Processar contatos
        try:
            dados['contatos'] = json.loads(request.form.get('contatos_json', '[]'))
        except:
            pass
        
        # Processar produtos
        try:
            dados['produtos'] = json.loads(request.form.get('produtos_json', '[]'))
        except:
            pass
        
        ClienteModel.create(dados)
        flash('Cliente criado com sucesso!', 'success')
        return redirect(url_for('clientes.lista'))
    return render_template('clientes/form.html')

@clientes_bp.route('/editar/<int:cliente_id>', methods=['GET', 'POST'])
@admin_required
def editar(cliente_id):
    cliente = ClienteModel.get_by_id(cliente_id)
    if not cliente:
        flash('Cliente não encontrado', 'error')
        return redirect(url_for('clientes.lista'))
    
    if request.method == 'POST':
        # Validar CNPJ/CPF
        cnpj = request.form.get('cnpj', '').strip()
        tipo_pessoa = request.form.get('tipo_pessoa', 'juridica')
        
        if cnpj:
            cnpj_limpo = limpar_documento(cnpj)
            if tipo_pessoa == 'juridica':
                if not validar_cnpj(cnpj_limpo):
                    flash('CNPJ inválido!', 'error')
                    return redirect(url_for('clientes.editar', cliente_id=cliente_id))
            else:
                if not validar_cpf(cnpj_limpo):
                    flash('CPF inválido!', 'error')
                    return redirect(url_for('clientes.editar', cliente_id=cliente_id))
        
        dados = {
            'nome': request.form.get('nome'),
            'razao_social': request.form.get('razao_social'),
            'cnpj': cnpj,
            'tipo_pessoa': tipo_pessoa,
            'email': request.form.get('email'),
            'telefone': request.form.get('telefone'),
            'cep': request.form.get('cep'),
            'logradouro': request.form.get('logradouro'),  # Form field name
            'numero': request.form.get('numero'),
            'complemento': request.form.get('complemento'),
            'bairro': request.form.get('bairro'),
            'cidade': request.form.get('cidade'),
            'uf': request.form.get('uf'),  # Form field name
            'contatos': [],
            'produtos': []
        }
        
        # Processar contatos e produtos
        try:
            dados['contatos'] = json.loads(request.form.get('contatos_json', '[]'))
        except:
            pass
        
        try:
            dados['produtos'] = json.loads(request.form.get('produtos_json', '[]'))
        except:
            pass
        
        ClienteModel.update(cliente_id, dados)
        flash('Cliente atualizado com sucesso!', 'success')
        return redirect(url_for('clientes.lista'))
    
    # Preparar dados para edição - converter Decimal, datetime e None para tipos compatíveis com JSON
    contatos = cliente.get('contatos', [])
    produtos = cliente.get('produtos', [])
    
    # Limpar os dados para serialização JSON
    for contato in contatos:
        # Remover campos datetime que não são necessários no formulário
        contato.pop('created_at', None)
    
    for produto in produtos:
        if 'valor' in produto and produto['valor'] is not None:
            produto['valor'] = float(produto['valor'])
        # Remover campos datetime
        produto.pop('created_at', None)
    
    contatos_json = json.dumps(contatos, ensure_ascii=False)
    produtos_json = json.dumps(produtos, ensure_ascii=False)
    
    return render_template('clientes/form.html', cliente=cliente, contatos_json=contatos_json, produtos_json=produtos_json)

@clientes_bp.route('/deletar/<int:cliente_id>', methods=['POST'])
@admin_required
def deletar(cliente_id):
    try:
        ClienteModel.delete(cliente_id)
        return jsonify({'success': True, 'message': 'Cliente desativado'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@clientes_bp.route('/toggle-status/<int:cliente_id>', methods=['POST'])
@admin_required
def toggle_status(cliente_id):
    try:
        ClienteModel.toggle_status(cliente_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
