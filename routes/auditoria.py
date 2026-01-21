"""
Rotas de Auditoria - Visualização de Logs do Sistema
"""
from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from functools import wraps
from models.auditoria import AuditoriaModel
from datetime import datetime, timedelta

auditoria_bp = Blueprint('auditoria', __name__, url_prefix='/auditoria')

def admin_required(f):
    """Decorator para restringir acesso a admins"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash('Por favor, faça login para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        
        if session.get('role') != 'admin':
            flash('Acesso negado. Esta página é restrita a administradores.', 'error')
            return redirect(url_for('dashboard.index'))
        
        return f(*args, **kwargs)
    return decorated_function

@auditoria_bp.route('/')
@admin_required
def index():
    """Página principal de auditoria com filtros"""
    # Obter parâmetros de filtro
    filtros = {}
    
    tabela = request.args.get('tabela')
    acao = request.args.get('acao')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    usuario_id = request.args.get('usuario_id')
    
    if tabela:
        filtros['tabela'] = tabela
    if acao:
        filtros['acao'] = acao
    if data_inicio:
        filtros['data_inicio'] = data_inicio
    if data_fim:
        filtros['data_fim'] = data_fim
    if usuario_id:
        filtros['usuario_id'] = int(usuario_id)
    
    # Paginação
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    offset = (page - 1) * per_page
    
    # Buscar logs
    logs = AuditoriaModel.listar_logs(filtros, limit=per_page, offset=offset)
    total = AuditoriaModel.contar_logs(filtros)
    total_pages = (total + per_page - 1) // per_page
    
    # Obter estatísticas
    estatisticas = AuditoriaModel.obter_estatisticas()
    
    return render_template('auditoria/index.html',
                         logs=logs,
                         filtros=filtros,
                         page=page,
                         total_pages=total_pages,
                         total=total,
                         per_page=per_page,
                         estatisticas=estatisticas)

@auditoria_bp.route('/historico/<tabela>/<int:registro_id>')
@admin_required
def historico_registro(tabela, registro_id):
    """Visualiza histórico completo de um registro"""
    historico = AuditoriaModel.obter_historico_registro(tabela, registro_id)
    
    return render_template('auditoria/historico.html',
                         historico=historico,
                         tabela=tabela,
                         registro_id=registro_id)

@auditoria_bp.route('/usuario/<int:usuario_id>')
@admin_required
def atividade_usuario(usuario_id):
    """Visualiza atividades de um usuário específico"""
    limit = int(request.args.get('limit', 100))
    atividades = AuditoriaModel.obter_atividade_usuario(usuario_id, limit)
    
    return render_template('auditoria/usuario.html',
                         atividades=atividades,
                         usuario_id=usuario_id)

@auditoria_bp.route('/estatisticas')
@admin_required
def estatisticas():
    """Dashboard com estatísticas de auditoria"""
    stats = AuditoriaModel.obter_estatisticas()
    
    return render_template('auditoria/estatisticas.html',
                         estatisticas=stats)

@auditoria_bp.route('/api/logs')
@admin_required
def api_logs():
    """API para buscar logs (para uso com DataTables, etc)"""
    filtros = {}
    
    tabela = request.args.get('tabela')
    acao = request.args.get('acao')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    usuario_id = request.args.get('usuario_id')
    
    if tabela:
        filtros['tabela'] = tabela
    if acao:
        filtros['acao'] = acao
    if data_inicio:
        filtros['data_inicio'] = data_inicio
    if data_fim:
        filtros['data_fim'] = data_fim
    if usuario_id:
        filtros['usuario_id'] = int(usuario_id)
    
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    offset = (page - 1) * per_page
    
    logs = AuditoriaModel.listar_logs(filtros, limit=per_page, offset=offset)
    total = AuditoriaModel.contar_logs(filtros)
    
    # Converter datetime para string
    for log in logs:
        if log.get('data_hora'):
            log['data_hora'] = log['data_hora'].isoformat()
    
    return jsonify({
        'logs': logs,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page
    })

@auditoria_bp.route('/minha-atividade')
def minha_atividade():
    """Permite que qualquer usuário veja sua própria atividade"""
    if 'user' not in session:
        flash('Por favor, faça login para acessar esta página.', 'warning')
        return redirect(url_for('login'))
    
    usuario_id = session.get('user_id')
    limit = int(request.args.get('limit', 50))
    
    atividades = AuditoriaModel.obter_atividade_usuario(usuario_id, limit)
    
    return render_template('auditoria/minha_atividade.html',
                         atividades=atividades)
