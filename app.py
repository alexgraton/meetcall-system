from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from datetime import datetime
import os
from config import Config
from database import db

# Importar blueprints
from routes.filiais import filiais_bp
from routes.tipos_servicos import tipos_servicos_bp
from routes.fornecedores import fornecedores_bp
from routes.clientes import clientes_bp
from routes.centro_custos import centro_custos_bp
from routes.plano_contas import plano_contas_bp
from routes.contas_pagar import contas_pagar_bp
from routes.contas_receber import contas_receber_bp
from routes.lancamentos import lancamentos_bp
from routes.contas_bancarias import contas_bancarias_bp
from routes.fluxo_caixa import fluxo_caixa_bp
from routes.dashboard import dashboard_bp
from routes.relatorios import relatorios_bp
from routes.conciliacao import conciliacao_bp
from routes.capacity import capacity_bp
from routes.margem import margem_bp

# Inicializar Flask com configurações
config = Config()
app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# Filtro customizado para formatação monetária
@app.template_filter('moeda')
def formatar_moeda(valor):
    """Formata valor numérico como moeda brasileira (R$ 1.234,56)"""
    if valor is None:
        valor = 0
    return f"{float(valor):,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

# Filtro customizado para formatação de data
@app.template_filter('date_format')
def formatar_data(valor):
    """Formata data no formato DD/MM/YYYY"""
    if valor is None:
        return ''
    if isinstance(valor, str):
        try:
            valor = datetime.strptime(valor, '%Y-%m-%d')
        except:
            return valor
    return valor.strftime('%d/%m/%Y')

# Registrar blueprints
app.register_blueprint(filiais_bp)
app.register_blueprint(tipos_servicos_bp)
app.register_blueprint(fornecedores_bp)
app.register_blueprint(clientes_bp)
app.register_blueprint(centro_custos_bp)
app.register_blueprint(plano_contas_bp)
app.register_blueprint(contas_pagar_bp)
app.register_blueprint(contas_receber_bp)
app.register_blueprint(lancamentos_bp)
app.register_blueprint(contas_bancarias_bp)
app.register_blueprint(fluxo_caixa_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(relatorios_bp)
app.register_blueprint(conciliacao_bp)
app.register_blueprint(capacity_bp)
app.register_blueprint(margem_bp)

# Decorator para rotas protegidas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Decorator para rotas que exigem permissão de admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        
        if session.get('role') != 'admin':
            flash('Você não tem permissão para acessar esta página.', 'error')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            user = db.authenticate_user(email, password)
            
            if user:
                session['user'] = user['email']
                session['user_id'] = user['id']
                session['name'] = user['name']
                session['role'] = user['role']
                flash(f'Bem-vindo(a), {user["name"]}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Email ou senha inválidos.', 'error')
                
        except Exception as e:
            flash('Erro interno do servidor. Tente novamente.', 'error')
            print(f"Erro na autenticação: {e}")
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """Redireciona para o Dashboard Financeiro"""
    return redirect(url_for('dashboard.index'))

@app.route('/cadastros')
@login_required
@admin_required
def cadastros():
    """Página de gerenciamento de usuários (apenas admin)"""
    users = db.get_all_users()
    return render_template('cadastros.html', users=users)

@app.route('/cadastros/novo', methods=['POST'])
@admin_required
def criar_usuario():
    """Cria um novo usuário"""
    try:
        email = request.form.get('email', '').strip()
        name = request.form.get('name', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', 'user')
        
        # Validações
        if not email or not name or not password:
            flash('Todos os campos são obrigatórios!', 'error')
            return redirect(url_for('cadastros'))
        
        if len(password) < 6:
            flash('A senha deve ter no mínimo 6 caracteres!', 'error')
            return redirect(url_for('cadastros'))
        
        if role not in ['admin', 'user']:
            role = 'user'
        
        # Cria o usuário
        user_id = db.create_user(email, password, name, role)
        flash(f'Usuário {name} criado com sucesso!', 'success')
        
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(f'Erro ao criar usuário: {str(e)}', 'error')
    
    return redirect(url_for('cadastros'))

@app.route('/cadastros/editar/<int:user_id>', methods=['POST'])
@admin_required
def editar_usuario(user_id):
    """Edita um usuário existente"""
    try:
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        role = request.form.get('role', 'user')
        
        if not name or not email:
            flash('Nome e email são obrigatórios!', 'error')
            return redirect(url_for('cadastros'))
        
        if role not in ['admin', 'user']:
            role = 'user'
        
        # Não permitir que o usuário remova o próprio admin
        if user_id == session.get('user_id') and role != 'admin':
            flash('Você não pode remover sua própria permissão de administrador!', 'error')
            return redirect(url_for('cadastros'))
        
        db.update_user(user_id, name=name, email=email, role=role)
        flash('Usuário atualizado com sucesso!', 'success')
        
        # Atualiza a sessão se for o próprio usuário
        if user_id == session.get('user_id'):
            session['name'] = name
            session['user'] = email
        
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(f'Erro ao editar usuário: {str(e)}', 'error')
    
    return redirect(url_for('cadastros'))

@app.route('/cadastros/toggle/<int:user_id>', methods=['POST'])
@admin_required
def toggle_usuario(user_id):
    """Ativa ou desativa um usuário"""
    try:
        # Não permitir desativar o próprio usuário
        if user_id == session.get('user_id'):
            flash('Você não pode desativar sua própria conta!', 'error')
            return redirect(url_for('cadastros'))
        
        db.toggle_user_status(user_id)
        flash('Status do usuário alterado com sucesso!', 'success')
        
    except Exception as e:
        flash(f'Erro ao alterar status: {str(e)}', 'error')
    
    return redirect(url_for('cadastros'))

@app.route('/cadastros/resetar-senha/<int:user_id>', methods=['POST'])
@admin_required
def resetar_senha(user_id):
    """Reseta a senha de um usuário"""
    try:
        nova_senha = request.form.get('nova_senha', '').strip()
        
        if not nova_senha or len(nova_senha) < 6:
            flash('A senha deve ter no mínimo 6 caracteres!', 'error')
            return redirect(url_for('cadastros'))
        
        user = db.get_user_by_id(user_id)
        if user:
            db.update_user_password(user['email'], nova_senha)
            flash(f'Senha de {user["name"]} resetada com sucesso!', 'success')
        else:
            flash('Usuário não encontrado!', 'error')
        
    except Exception as e:
        flash(f'Erro ao resetar senha: {str(e)}', 'error')
    
    return redirect(url_for('cadastros'))

@app.route('/configuracoes')
@admin_required
def configuracoes():
    # Buscar todos os usuários
    users = db.get_all_users()
    return render_template('configuracoes.html', users=users)

@app.route('/configuracoes/usuario', methods=['POST'])
@admin_required
def manage_user():
    """Cadastrar ou editar usuário"""
    user_id = request.form.get('user_id')
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role')
    
    try:
        if user_id:  # Editar usuário existente
            db.update_user(int(user_id), name=name, email=email, role=role)
            if password:  # Se forneceu senha, atualiza também
                db.update_user_password_by_id(int(user_id), password)
            flash('Usuário atualizado com sucesso!', 'success')
        else:  # Cadastrar novo usuário
            if not password:
                flash('Senha é obrigatória para novo usuário!', 'error')
                return redirect(url_for('configuracoes'))
            
            db.create_user(email, password, name, role)
            flash('Usuário cadastrado com sucesso!', 'success')
    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(f'Erro ao salvar usuário: {str(e)}', 'error')
    
    return redirect(url_for('configuracoes'))

@app.route('/configuracoes/alterar-senha', methods=['POST'])
@login_required
def change_password():
    """Alterar senha do usuário logado"""
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    
    if new_password != confirm_password:
        flash('As senhas não coincidem!', 'error')
        return redirect(url_for('configuracoes'))
    
    # Verificar senha atual
    user = db.authenticate_user(session['email'], current_password)
    if not user:
        flash('Senha atual incorreta!', 'error')
        return redirect(url_for('configuracoes'))
    
    # Atualizar senha
    try:
        db.update_user_password(session['email'], new_password)
        flash('Senha alterada com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao alterar senha: {str(e)}', 'error')
    
    return redirect(url_for('configuracoes'))

@app.route('/configuracoes/resetar-senha', methods=['POST'])
@admin_required
def reset_user_password():
    """Resetar senha de um usuário (apenas admin)"""
    user_id = request.form.get('user_id')
    new_password = request.form.get('new_password')
    
    try:
        db.update_user_password_by_id(int(user_id), new_password)
        flash('Senha resetada com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao resetar senha: {str(e)}', 'error')
    
    return redirect(url_for('configuracoes'))

@app.route('/configuracoes/backup', methods=['POST'])
@admin_required
def backup_database():
    """Gerar backup do banco de dados"""
    import subprocess
    from flask import send_file
    import tempfile
    from datetime import datetime
    
    try:
        # Criar arquivo temporário para o backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(tempfile.gettempdir(), f'backup_{timestamp}.sql')
        
        # Obter configurações do banco
        mysql_config = config.MYSQL_CONFIG
        
        # Comando mysqldump
        cmd = [
            'mysqldump',
            '-h', mysql_config['host'],
            '-u', mysql_config['user'],
            f'-p{mysql_config["password"]}',
            mysql_config['database'],
            '--result-file=' + backup_file
        ]
        
        # Executar mysqldump
        subprocess.run(cmd, check=True, capture_output=True)
        
        # Enviar arquivo para download
        return send_file(
            backup_file,
            as_attachment=True,
            download_name=f'backup_{timestamp}.sql',
            mimetype='application/sql'
        )
    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'Erro ao executar mysqldump. Verifique se está instalado.'}), 500
    except Exception as e:
        return jsonify({'error': f'Erro ao gerar backup: {str(e)}'}), 500

@app.route('/perfil')
@login_required
def perfil():
    return render_template('perfil.html')

@app.route('/logout')
@login_required
def logout():
    name = session.get('name', 'Usuário')
    session.clear()
    flash(f'Até logo, {name}!', 'info')
    return redirect(url_for('login'))

# Função para verificar se o banco está configurado corretamente
def check_database_connection():
    """Verifica se a conexão com o banco de dados está funcionando"""
    try:
        with db.get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            return True
    except Exception as e:
        print(f"Erro de conexão com o banco: {e}")
        return False

# Rota para testar conexão com banco (remover em produção)
@app.route('/test-db')
def test_database():
    if check_database_connection():
        return "✅ Conexão com banco de dados OK!"
    else:
        return "❌ Falha na conexão com banco de dados!", 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
