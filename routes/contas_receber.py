"""
Rotas para gerenciamento de Contas a Receber
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from functools import wraps
from datetime import datetime, date
from decimal import Decimal
from models.conta_receber import ContaReceberModel
from models.cliente import ClienteModel
from models.tipo_servico import TipoServicoModel
from models.centro_custo import CentroCustoModel
from models.plano_conta import PlanoContaModel
from models.filial import FilialModel

contas_receber_bp = Blueprint('contas_receber', __name__, url_prefix='/contas-receber')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('Acesso negado. Apenas administradores podem acessar esta página.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@contas_receber_bp.route('/')
@login_required
@admin_required
def lista():
    # Filtros
    cliente_id = request.args.get('cliente_id', type=int)
    filial_id = request.args.get('filial_id', type=int)
    status = request.args.get('status')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    # Converter datas
    data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date() if data_inicio else None
    data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date() if data_fim else None
    
    # Buscar contas
    contas = ContaReceberModel.get_all(
        cliente_id=cliente_id,
        filial_id=filial_id,
        status=status,
        data_inicio=data_inicio_obj,
        data_fim=data_fim_obj
    )
    
    # Buscar dados para filtros
    clientes = ClienteModel.get_all()
    filiais = FilialModel.get_all()
    
    # Calcular totalizadores
    totalizadores = ContaReceberModel.get_totalizadores()
    
    return render_template('contas_receber/lista.html',
                         contas=contas,
                         clientes=clientes,
                         filiais=filiais,
                         totalizadores=totalizadores,
                         filtros={
                             'cliente_id': cliente_id,
                             'filial_id': filial_id,
                             'status': status,
                             'data_inicio': data_inicio,
                             'data_fim': data_fim
                         })

@contas_receber_bp.route('/nova', methods=['GET', 'POST'])
@login_required
@admin_required
def nova():
    if request.method == 'POST':
        try:
            # Coletar dados do formulário
            dados = {
                'cliente_id': int(request.form['cliente_id']),
                'filial_id': int(request.form['filial_id']) if request.form.get('filial_id') else None,
                'tipo_servico_id': int(request.form['tipo_servico_id']) if request.form.get('tipo_servico_id') else None,
                'centro_custo_id': int(request.form['centro_custo_id']) if request.form.get('centro_custo_id') else None,
                'conta_contabil_id': int(request.form['conta_contabil_id']) if request.form.get('conta_contabil_id') else None,
                'descricao': request.form['descricao'],
                'numero_documento': request.form.get('numero_documento'),
                'valor_total': Decimal(request.form['valor_total']),
                'data_emissao': datetime.strptime(request.form['data_emissao'], '%Y-%m-%d').date(),
                'data_vencimento': datetime.strptime(request.form['data_vencimento'], '%Y-%m-%d').date(),
                'numero_parcelas': int(request.form.get('numero_parcelas', 1)),
                'intervalo_parcelas': int(request.form.get('intervalo_parcelas', 30)),
                'percentual_juros': Decimal(request.form.get('percentual_juros', 0)),
                'percentual_multa': Decimal(request.form.get('percentual_multa', 0)),
                'is_recorrente': request.form.get('is_recorrente') == 'on',
                'recorrencia_tipo': request.form.get('recorrencia_tipo') if request.form.get('is_recorrente') else None,
                'observacoes': request.form.get('observacoes'),
                'created_by': session.get('user_id')
            }
            
            conta_id = ContaReceberModel.create(dados)
            
            if dados['numero_parcelas'] > 1:
                flash(f'Conta a receber criada com sucesso! {dados["numero_parcelas"]} parcelas geradas.', 'success')
            else:
                flash('Conta a receber criada com sucesso!', 'success')
            
            return redirect(url_for('contas_receber.lista'))
            
        except Exception as e:
            flash(f'Erro ao criar conta: {str(e)}', 'error')
    
    # GET - Exibir formulário
    clientes = ClienteModel.get_all()
    filiais = FilialModel.get_all()
    tipos_servicos = TipoServicoModel.get_all()
    centros_custos = CentroCustoModel.get_all()
    # Buscar apenas contas de receita
    plano_contas = PlanoContaModel.get_all()
    contas_receita = [c for c in plano_contas if c.get('tipo') == 'receita' and c.get('nivel') == 'analitica']
    
    return render_template('contas_receber/form.html',
                         clientes=clientes,
                         filiais=filiais,
                         tipos_servicos=tipos_servicos,
                         centros_custos=centros_custos,
                         plano_contas=contas_receita,
                         today=date.today().strftime('%Y-%m-%d'))

@contas_receber_bp.route('/<int:conta_id>/receber', methods=['GET', 'POST'])
@login_required
@admin_required
def receber(conta_id):
    conta = ContaReceberModel.get_by_id(conta_id)
    
    if not conta:
        flash('Conta não encontrada.', 'error')
        return redirect(url_for('contas_receber.lista'))
    
    if conta['status'] == 'recebido':
        flash('Esta conta já foi recebida.', 'warning')
        return redirect(url_for('contas_receber.detalhes', conta_id=conta_id))
    
    if request.method == 'POST':
        try:
            dados_recebimento = {
                'data_recebimento': datetime.strptime(request.form['data_recebimento'], '%Y-%m-%d').date(),
                'valor_pago': Decimal(request.form['valor_pago']),
                'valor_juros': Decimal(request.form.get('valor_juros', 0)),
                'valor_multa': Decimal(request.form.get('valor_multa', 0)),
                'valor_desconto': Decimal(request.form.get('valor_desconto', 0))
            }
            
            ContaReceberModel.receber(conta_id, dados_recebimento)
            flash('Recebimento registrado com sucesso!', 'success')
            return redirect(url_for('contas_receber.lista'))
            
        except Exception as e:
            flash(f'Erro ao registrar recebimento: {str(e)}', 'error')
    
    return render_template('contas_receber/receber.html',
                         conta=conta,
                         today=date.today().strftime('%Y-%m-%d'))

@contas_receber_bp.route('/<int:conta_id>/cancelar', methods=['POST'])
@login_required
@admin_required
def cancelar(conta_id):
    try:
        ContaReceberModel.cancelar(conta_id)
        flash('Conta cancelada com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao cancelar conta: {str(e)}', 'error')
    
    return redirect(url_for('contas_receber.lista'))

@contas_receber_bp.route('/<int:conta_id>')
@login_required
@admin_required
def detalhes(conta_id):
    conta = ContaReceberModel.get_by_id(conta_id)
    
    if not conta:
        flash('Conta não encontrada.', 'error')
        return redirect(url_for('contas_receber.lista'))
    
    return render_template('contas_receber/detalhes.html', conta=conta)

@contas_receber_bp.route('/api/calcular-juros/<int:conta_id>')
@login_required
def api_calcular_juros(conta_id):
    """API para calcular juros e multa em tempo real"""
    try:
        data_recebimento = request.args.get('data_recebimento')
        valor_desconto = Decimal(request.args.get('desconto', 0))
        
        conta = ContaReceberModel.get_by_id(conta_id)
        
        if not conta:
            return jsonify({'error': 'Conta não encontrada'}), 404
        
        data_receb = datetime.strptime(data_recebimento, '%Y-%m-%d').date()
        data_venc = conta['data_vencimento']
        
        dias_atraso = (data_receb - data_venc).days if data_receb > data_venc else 0
        
        valor_original = Decimal(str(conta['valor_total']))
        juros_dia = Decimal(str(conta['percentual_juros']))
        multa_perc = Decimal(str(conta['percentual_multa']))
        
        valor_multa = Decimal(0)
        valor_juros = Decimal(0)
        
        if dias_atraso > 0:
            valor_multa = (valor_original * multa_perc / 100)
            valor_juros = (valor_original * juros_dia / 100 * dias_atraso)
        
        valor_total = valor_original + valor_multa + valor_juros - valor_desconto
        
        return jsonify({
            'dias_atraso': dias_atraso,
            'valor_multa': float(valor_multa),
            'valor_juros': float(valor_juros),
            'valor_total': float(valor_total)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400
