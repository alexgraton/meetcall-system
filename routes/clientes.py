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
        
        # Padronizar nomes para Title Case
        nome = request.form.get('nome', '').strip()
        razao_social = request.form.get('razao_social', '').strip()
        
        dados = {
            'nome': nome.title() if nome else None,
            'razao_social': razao_social.title() if razao_social else None,
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
            'tipo_servico_id': request.form.get('tipo_servico_id'),
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
    
    # Buscar tipos de serviços (categorias) para o select
    from models.tipo_servico import TipoServicoModel
    tipos_servicos = TipoServicoModel.get_all()
    return render_template('clientes/form.html', tipos_servicos=tipos_servicos)

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
                    return redirect(url_for('clientes.novo'))
        
        # Padronizar nomes para Title Case
        nome = request.form.get('nome', '').strip()
        razao_social = request.form.get('razao_social', '').strip()
        
        dados = {
            'nome': nome.title() if nome else None,
            'razao_social': razao_social.title() if razao_social else None,
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
            'tipo_servico_id': request.form.get('tipo_servico_id'),
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
    
    # Buscar tipos de serviços (categorias) para o select
    from models.tipo_servico import TipoServicoModel
    tipos_servicos = TipoServicoModel.get_all()
    
    return render_template('clientes/form.html', cliente=cliente, contatos_json=contatos_json, produtos_json=produtos_json, tipos_servicos=tipos_servicos)

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

@clientes_bp.route('/<int:cliente_id>/contato/<int:contato_id>/deletar', methods=['POST'])
@admin_required
def deletar_contato(cliente_id, contato_id):
    """Deleta um contato específico de um cliente"""
    try:
        from database import DatabaseManager
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cliente_contatos WHERE id = %s AND cliente_id = %s", (contato_id, cliente_id))
            conn.commit()
            return jsonify({'success': True, 'message': 'Contato removido'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@clientes_bp.route('/<int:cliente_id>/contato/adicionar', methods=['POST'])
@admin_required
def adicionar_contato(cliente_id):
    """Adiciona um contato a um cliente existente"""
    try:
        from database import DatabaseManager
        data = request.get_json()
        
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO cliente_contatos (cliente_id, nome, telefone, email, cargo, observacoes)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                cliente_id,
                data.get('nome'),
                data.get('telefone'),
                data.get('email'),
                data.get('cargo'),
                data.get('observacoes')
            ))
            conn.commit()
            contato_id = cursor.lastrowid
            return jsonify({'success': True, 'message': 'Contato adicionado', 'id': contato_id})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@clientes_bp.route('/<int:cliente_id>/produto/<int:produto_id>/deletar', methods=['POST'])
@admin_required
def deletar_produto(cliente_id, produto_id):
    """Deleta um produto específico de um cliente"""
    try:
        from database import DatabaseManager
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cliente_produtos WHERE id = %s AND cliente_id = %s", (produto_id, cliente_id))
            conn.commit()
            return jsonify({'success': True, 'message': 'Produto removido'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@clientes_bp.route('/<int:cliente_id>/produto/adicionar', methods=['POST'])
@admin_required
def adicionar_produto(cliente_id):
    """Adiciona um produto a um cliente existente"""
    try:
        from database import DatabaseManager
        data = request.get_json()
        
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO cliente_produtos (cliente_id, nome, codigo, descricao, is_active)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                cliente_id,
                data.get('nome'),
                data.get('codigo'),
                data.get('descricao'),
                data.get('is_active', True)
            ))
            conn.commit()
            produto_id = cursor.lastrowid
            return jsonify({'success': True, 'message': 'Produto adicionado', 'id': produto_id})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
