from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'meetcall-secret-key-2025'  # Altere para uma chave segura em produção

# Simulação de banco de dados de usuários (use um banco real em produção)
USERS = {
    'admin@meetcall.com': {'password': 'admin123', 'name': 'Administrador'},
    'usuario@meetcall.com': {'password': 'user123', 'name': 'Usuário Teste'}
}

# Decorator para rotas protegidas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
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
        
        if email in USERS and USERS[email]['password'] == password:
            session['user'] = email
            session['name'] = USERS[email]['name']
            flash(f'Bem-vindo(a), {USERS[email]["name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Email ou senha inválidos.', 'error')
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Dados simulados para o dashboard
    dados = {
        'total_chamadas': 1247,
        'chamadas_hoje': 89,
        'tempo_medio': '12:34',
        'satisfacao': 4.5,
        'chamadas_recentes': [
            {'id': '#12345', 'cliente': 'João Silva', 'data': '16/10/2025 14:30', 'duracao': '15:23', 'status': 'Concluída'},
            {'id': '#12344', 'cliente': 'Maria Santos', 'data': '16/10/2025 13:15', 'duracao': '08:45', 'status': 'Concluída'},
            {'id': '#12343', 'cliente': 'Pedro Costa', 'data': '16/10/2025 12:00', 'duracao': '22:10', 'status': 'Concluída'},
            {'id': '#12342', 'cliente': 'Ana Oliveira', 'data': '16/10/2025 11:20', 'duracao': '05:32', 'status': 'Pendente'},
        ],
        'grafico_labels': ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'],
        'grafico_dados': [45, 52, 38, 67, 73, 28, 15]
    }
    return render_template('dashboard.html', dados=dados)

@app.route('/cadastros')
@login_required
def cadastros():
    return render_template('cadastros.html')

@app.route('/configuracoes')
@login_required
def configuracoes():
    return render_template('configuracoes.html')

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
