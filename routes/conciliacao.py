"""
Rotas para conciliação bancária
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models.conciliacao import Conciliacao
from werkzeug.utils import secure_filename
from utils.auditoria import auditar_agora
import os
import functools
from datetime import datetime


conciliacao_bp = Blueprint('conciliacao', __name__, url_prefix='/conciliacao')

# Configuração de upload
UPLOAD_FOLDER = 'uploads/extratos'
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

# Criar pasta de uploads se não existir
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def login_required(f):
    """Decorator para verificar se usuário está logado"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def allowed_file(filename):
    """Verifica se extensão do arquivo é permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@conciliacao_bp.route('/')
@login_required
def index():
    """Página principal de conciliação"""
    try:
        from database import DatabaseManager
        db = DatabaseManager()
        
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Buscar contas bancárias ativas
            cursor.execute("""
                SELECT id, banco, agencia, numero_conta, descricao, saldo_atual
                FROM contas_bancarias
                WHERE ativo = 1
                ORDER BY banco, agencia, numero_conta
            """)
            contas = cursor.fetchall()
            cursor.close()
        
        # Buscar últimas conciliações
        conciliacoes = Conciliacao.listar_conciliacoes(limit=10)
        
        return render_template('conciliacao/index.html',
                             contas=contas,
                             conciliacoes=conciliacoes)
    
    except Exception as e:
        flash(f'Erro ao carregar página: {str(e)}', 'error')
        return redirect(url_for('dashboard.index'))


@conciliacao_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    """Faz upload e processa arquivo de extrato"""
    try:
        # Validar arquivo
        if 'arquivo' not in request.files:
            flash('Nenhum arquivo foi enviado', 'error')
            return redirect(url_for('conciliacao.index'))
        
        arquivo = request.files['arquivo']
        
        if arquivo.filename == '':
            flash('Nenhum arquivo foi selecionado', 'error')
            return redirect(url_for('conciliacao.index'))
        
        if not allowed_file(arquivo.filename):
            flash('Formato de arquivo não permitido. Use Excel (.xlsx)', 'error')
            return redirect(url_for('conciliacao.index'))
        
        # Validar conta bancária
        conta_bancaria_id = request.form.get('conta_bancaria_id')
        if not conta_bancaria_id:
            flash('Selecione uma conta bancária', 'error')
            return redirect(url_for('conciliacao.index'))
        
        # Salvar arquivo
        filename = secure_filename(arquivo.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename_final = f"{timestamp}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, filename_final)
        arquivo.save(filepath)
        
        # Importar parsers do sistema
        import sys
        sys.path.append(os.path.dirname(os.path.dirname(__file__)))
        from services.parsers_extrato import detectar_banco, criar_parser
        
        # Detectar banco e criar parser apropriado
        banco_detectado = detectar_banco(filepath)
        
        if not banco_detectado:
            flash('Não foi possível identificar o formato do arquivo. Certifique-se de usar um extrato do Itaú ou Banco do Brasil.', 'error')
            os.remove(filepath)
            return redirect(url_for('conciliacao.index'))
        
        # Criar parser e processar arquivo
        parser = criar_parser(filepath)
        transacoes_parsed = parser.parse()
        
        if not transacoes_parsed or len(transacoes_parsed) == 0:
            flash('Nenhuma transação foi encontrada no arquivo', 'warning')
            os.remove(filepath)
            return redirect(url_for('conciliacao.index'))
        
        # Converter para formato esperado pela conciliação
        transacoes = []
        for trans in transacoes_parsed:
            transacoes.append({
                'data_transacao': trans['data_lancamento'],
                'descricao': trans['historico'],
                'documento': trans.get('documento', ''),
                'valor': abs(float(trans['valor'])),
                'tipo': trans['tipo_movimento'],  # já vem como 'credito' ou 'debito'
                'saldo_apos': float(trans.get('saldo_apos', 0)) if trans.get('saldo_apos') else None
            })
        
        # Criar conciliação
        conciliacao_id = Conciliacao.criar_conciliacao(
            conta_bancaria_id=conta_bancaria_id,
            nome_arquivo=filename,
            transacoes=transacoes,
            user_id=session.get('user_id')
        )
        
        flash(f'Extrato importado com sucesso! {len(transacoes)} transações processadas.', 'success')
        return redirect(url_for('conciliacao.matching', conciliacao_id=conciliacao_id))
    
    except Exception as e:
        flash(f'Erro ao processar arquivo: {str(e)}', 'error')
        return redirect(url_for('conciliacao.index'))


@conciliacao_bp.route('/matching/<int:conciliacao_id>')
@login_required
def matching(conciliacao_id):
    """Página de matching automático/manual"""
    try:
        # Buscar detalhes da conciliação
        conciliacao = Conciliacao.get_detalhes_conciliacao(conciliacao_id)
        
        if not conciliacao:
            flash('Conciliação não encontrada', 'error')
            return redirect(url_for('conciliacao.index'))
        
        # Buscar matches automáticos
        matches = Conciliacao.buscar_matches_automaticos(conciliacao_id)
        
        # Agrupar matches por transação do extrato
        matches_por_transacao = {}
        transacoes_com_match_ids = set()
        
        for match in matches:
            trans_id = match['transacao_extrato_id']
            transacoes_com_match_ids.add(trans_id)
            if trans_id not in matches_por_transacao:
                matches_por_transacao[trans_id] = []
            matches_por_transacao[trans_id].append(match)
        
        # Ordenar matches dentro de cada transação por similaridade
        for trans_id in matches_por_transacao:
            matches_por_transacao[trans_id].sort(key=lambda x: x['similaridade'], reverse=True)
        
        # Separar transações COM e SEM matches
        transacoes_com_match = []
        transacoes_sem_match = []
        
        for trans in conciliacao['transacoes']:
            if trans['status_conciliacao'] == 'conciliada':
                continue  # Pular transações já conciliadas
            
            if trans['id'] in transacoes_com_match_ids:
                # Adicionar com a maior similaridade para ordenação
                max_similaridade = matches_por_transacao[trans['id']][0]['similaridade']
                transacoes_com_match.append({
                    'transacao': trans,
                    'max_similaridade': max_similaridade
                })
            else:
                transacoes_sem_match.append(trans)
        
        # Ordenar transações com match por maior similaridade
        transacoes_com_match.sort(key=lambda x: x['max_similaridade'], reverse=True)
        
        # Reconstruir lista de transações: com match primeiro, depois sem match
        transacoes_ordenadas = [item['transacao'] for item in transacoes_com_match] + transacoes_sem_match
        
        # Atualizar a lista de transações na conciliação
        conciliacao['transacoes'] = transacoes_ordenadas
        
        return render_template('conciliacao/matching.html',
                             conciliacao=conciliacao,
                             matches_por_transacao=matches_por_transacao)
    
    except Exception as e:
        flash(f'Erro ao carregar página: {str(e)}', 'error')
        return redirect(url_for('conciliacao.index'))


@conciliacao_bp.route('/conciliar', methods=['POST'])
@login_required
def conciliar():
    """Executa conciliação manual"""
    try:
        transacao_extrato_id = request.form.get('transacao_extrato_id')
        tipo_transacao = request.form.get('tipo_transacao')
        transacao_id = request.form.get('transacao_id')
        conciliacao_id = request.form.get('conciliacao_id')
        
        if not all([transacao_extrato_id, tipo_transacao, transacao_id]):
            flash('Dados incompletos para conciliação', 'error')
            return redirect(url_for('conciliacao.matching', conciliacao_id=conciliacao_id))
        
        Conciliacao.conciliar_transacao(
            transacao_extrato_id=transacao_extrato_id,
            tipo_transacao=tipo_transacao,
            transacao_id=transacao_id,
            user_id=session.get('user_id')
        )
        
        flash('Transação conciliada com sucesso!', 'success')
        return redirect(url_for('conciliacao.matching', conciliacao_id=conciliacao_id))
    
    except Exception as e:
        flash(f'Erro ao conciliar: {str(e)}', 'error')
        return redirect(url_for('conciliacao.matching', conciliacao_id=conciliacao_id))


@conciliacao_bp.route('/desconciliar', methods=['POST'])
@login_required
def desconciliar():
    """Remove conciliação de uma transação"""
    try:
        transacao_extrato_id = request.form.get('transacao_extrato_id')
        conciliacao_id = request.form.get('conciliacao_id')
        
        if not transacao_extrato_id:
            flash('ID da transação não informado', 'error')
            return redirect(url_for('conciliacao.matching', conciliacao_id=conciliacao_id))
        
        Conciliacao.desconciliar_transacao(transacao_extrato_id)
        
        flash('Conciliação removida com sucesso!', 'success')
        return redirect(url_for('conciliacao.matching', conciliacao_id=conciliacao_id))
    
    except Exception as e:
        flash(f'Erro ao desconciliar: {str(e)}', 'error')
        return redirect(url_for('conciliacao.matching', conciliacao_id=conciliacao_id))


@conciliacao_bp.route('/historico')
@login_required
def historico():
    """Histórico de conciliações"""
    try:
        conta_id = request.args.get('conta_id', type=int)
        conciliacoes = Conciliacao.listar_conciliacoes(conta_bancaria_id=conta_id, limit=50)
        
        return render_template('conciliacao/historico.html',
                             conciliacoes=conciliacoes,
                             conta_id=conta_id)
    
    except Exception as e:
        flash(f'Erro ao carregar histórico: {str(e)}', 'error')
        return redirect(url_for('conciliacao.index'))


@conciliacao_bp.route('/detalhes/<int:conciliacao_id>')
@login_required
def detalhes(conciliacao_id):
    """Detalhes de uma conciliação específica"""
    try:
        conciliacao = Conciliacao.get_detalhes_conciliacao(conciliacao_id)
        
        if not conciliacao:
            flash('Conciliação não encontrada', 'error')
            return redirect(url_for('conciliacao.historico'))
        
        return render_template('conciliacao/detalhes.html',
                             conciliacao=conciliacao)
    
    except Exception as e:
        flash(f'Erro ao carregar detalhes: {str(e)}', 'error')
        return redirect(url_for('conciliacao.historico'))


# API JSON
@conciliacao_bp.route('/api/matches/<int:conciliacao_id>')
@login_required
def api_matches(conciliacao_id):
    """Retorna matches em JSON"""
    try:
        tolerancia_dias = request.args.get('tolerancia_dias', 3, type=int)
        tolerancia_valor = request.args.get('tolerancia_valor', 0.01, type=float)
        
        matches = Conciliacao.buscar_matches_automaticos(
            conciliacao_id, 
            tolerancia_dias=tolerancia_dias,
            tolerancia_valor=tolerancia_valor
        )
        
        # Converter Decimal para float
        for match in matches:
            for key, value in match['transacao_extrato'].items():
                if hasattr(value, 'as_integer_ratio'):  # É Decimal
                    match['transacao_extrato'][key] = float(value)
            for key, value in match['transacao_sistema'].items():
                if value and hasattr(value, 'as_integer_ratio'):
                    match['transacao_sistema'][key] = float(value)
        
        return jsonify(matches)
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500
