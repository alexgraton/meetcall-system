"""
Rotas para gerenciamento de Contas a Pagar
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from functools import wraps
from datetime import datetime, date
from decimal import Decimal
from models.conta_pagar import ContaPagarModel
from models.fornecedor import FornecedorModel
from models.tipo_servico import TipoServicoModel
from models.centro_custo import CentroCustoModel
from models.plano_conta import PlanoContaModel
from models.filial import FilialModel

contas_pagar_bp = Blueprint('contas_pagar', __name__, url_prefix='/contas-pagar')

def converter_valor_brasileiro(valor_str):
    """Converte valor formatado em pt-BR (1.500,00) para Decimal"""
    if not valor_str:
        return 0
    # Remove pontos (separador de milhar) e substitui vírgula por ponto
    from decimal import Decimal
    valor_limpo = valor_str.replace('.', '').replace(',', '.')
    return Decimal(valor_limpo)

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

@contas_pagar_bp.route('/')
@login_required
@admin_required
def lista():
    # Filtros
    fornecedor_id = request.args.get('fornecedor_id', type=int)
    filial_id = request.args.get('filial_id', type=int)
    status = request.args.get('status')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    # Converter datas
    data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date() if data_inicio else None
    data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date() if data_fim else None
    
    # Buscar contas
    contas = ContaPagarModel.get_all(
        fornecedor_id=fornecedor_id,
        filial_id=filial_id,
        status=status,
        data_inicio=data_inicio_obj,
        data_fim=data_fim_obj
    )
    
    # Buscar dados para filtros
    fornecedores = FornecedorModel.get_all()
    filiais = FilialModel.get_all()
    
    # Totalizadores
    totalizadores = ContaPagarModel.get_totalizadores({
        'fornecedor_id': fornecedor_id,
        'filial_id': filial_id
    })
    
    return render_template('contas_pagar/lista.html', 
                         contas=contas,
                         fornecedores=fornecedores,
                         filiais=filiais,
                         totalizadores=totalizadores,
                         filtros={
                             'fornecedor_id': fornecedor_id,
                             'filial_id': filial_id,
                             'status': status,
                             'data_inicio': data_inicio,
                             'data_fim': data_fim
                         })

@contas_pagar_bp.route('/nova', methods=['GET', 'POST'])
@login_required
@admin_required
def nova():
    if request.method == 'POST':
        dados = {
            'fornecedor_id': request.form.get('fornecedor_id'),
            'tipo_servico_id': request.form.get('tipo_servico_id') or None,
            'centro_custo_id': request.form.get('centro_custo_id') or None,
            'conta_contabil_id': request.form.get('conta_contabil_id') or None,
            'filial_id': request.form.get('filial_id') or None,
            'descricao': request.form.get('descricao'),
            'numero_documento': request.form.get('numero_documento'),
            'observacoes': request.form.get('observacoes'),
            'valor_total': converter_valor_brasileiro(request.form.get('valor_total')),
            'numero_parcelas': int(request.form.get('numero_parcelas', 1)),
            'recorrente': request.form.get('recorrente') == 'on',
            'tipo_recorrencia': request.form.get('tipo_recorrencia') or None,
            'data_emissao': request.form.get('data_emissao'),
            'data_vencimento': request.form.get('data_vencimento'),
            'percentual_juros': request.form.get('percentual_juros', 0),
            'percentual_multa': request.form.get('percentual_multa', 0),
            'created_by': session.get('user_id')
        }
        
        resultado = ContaPagarModel.create(dados)
        
        if resultado['success']:
            flash(resultado['message'], 'success')
            return redirect(url_for('contas_pagar.lista'))
        else:
            flash(f"Erro ao criar conta: {resultado['message']}", 'error')
    
    # Dados para o formulário
    fornecedores = FornecedorModel.get_all()
    tipos_servicos = TipoServicoModel.get_all()
    centros_custos = CentroCustoModel.get_all()
    contas_analiticas = PlanoContaModel.get_analiticas(tipo='despesa')
    filiais = FilialModel.get_all()
    
    return render_template('contas_pagar/form.html',
                         fornecedores=fornecedores,
                         tipos_servicos=tipos_servicos,
                         centros_custos=centros_custos,
                         contas_analiticas=contas_analiticas,
                         filiais=filiais)

@contas_pagar_bp.route('/baixar/<int:conta_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def baixar(conta_id):
    if request.method == 'POST':
        try:
            # Validar conta bancária
            if not request.form.get('conta_bancaria_id'):
                flash('Conta bancária é obrigatória para registrar pagamento!', 'error')
                return redirect(url_for('contas_pagar.baixar', conta_id=conta_id))
            
            # Converter valores com tratamento de campos vazios
            valor_desconto_str = request.form.get('valor_desconto', '0').strip()
            valor_desconto = valor_desconto_str if valor_desconto_str and valor_desconto_str != '' else '0'
            
            dados_baixa = {
                'conta_bancaria_id': int(request.form['conta_bancaria_id']),
                'data_pagamento': request.form.get('data_pagamento'),
                'valor_desconto': valor_desconto
            }
            
            # Registrar baixa na conta a pagar
            resultado = ContaPagarModel.baixar(conta_id, dados_baixa)
            
            if resultado['success']:
                # Movimentar conta bancária (debitar)
                from models.conta_bancaria import ContaBancariaModel
                try:
                    ContaBancariaModel.debitar(
                        dados_baixa['conta_bancaria_id'],
                        Decimal(str(resultado['valor_pago']))
                    )
                    flash(f"✅ {resultado['message']} Saldo da conta bancária atualizado.", 'success')
                except ValueError as e:
                    flash(f"⚠️ Pagamento registrado, mas erro ao atualizar saldo: {str(e)}", 'warning')
            else:
                flash(f"Erro ao registrar pagamento: {resultado['message']}", 'error')
            
        except Exception as e:
            flash(f"Erro ao processar pagamento: {str(e)}", 'error')
        
        return redirect(url_for('contas_pagar.lista'))
    
    # GET - mostrar formulário de baixa
    conta = ContaPagarModel.get_by_id(conta_id)
    if not conta:
        flash('Conta não encontrada', 'error')
        return redirect(url_for('contas_pagar.lista'))
    
    # Buscar contas bancárias ativas
    from models.conta_bancaria import ContaBancariaModel
    contas_bancarias = ContaBancariaModel.get_all({'ativo': True})
    
    from datetime import date
    return render_template('contas_pagar/baixar.html', 
                         conta=conta, 
                         contas_bancarias=contas_bancarias,
                         today=date.today().strftime('%Y-%m-%d'))

@contas_pagar_bp.route('/cancelar/<int:conta_id>', methods=['POST'])
@login_required
@admin_required
def cancelar(conta_id):
    resultado = ContaPagarModel.cancelar(conta_id)
    return jsonify(resultado)

@contas_pagar_bp.route('/detalhes/<int:conta_id>')
@login_required
@admin_required
def detalhes(conta_id):
    conta = ContaPagarModel.get_by_id(conta_id)
    if not conta:
        flash('Conta não encontrada', 'error')
        return redirect(url_for('contas_pagar.lista'))
    
    return render_template('contas_pagar/detalhes.html', conta=conta)

@contas_pagar_bp.route('/api/calcular-juros/<int:conta_id>')
@login_required
def api_calcular_juros(conta_id):
    """API para calcular juros e multa em tempo real"""
    data_pagamento = request.args.get('data_pagamento')
    
    if not data_pagamento:
        return jsonify({'error': 'Data de pagamento não informada'}), 400
    
    conta = ContaPagarModel.get_by_id(conta_id)
    if not conta:
        return jsonify({'error': 'Conta não encontrada'}), 404
    
    # Calcular juros e multa
    from decimal import Decimal
    data_pagamento_obj = datetime.strptime(data_pagamento, '%Y-%m-%d').date()
    data_vencimento = conta['data_vencimento']
    
    valor_juros = 0
    valor_multa = 0
    dias_atraso = 0
    
    if data_pagamento_obj > data_vencimento:
        dias_atraso = (data_pagamento_obj - data_vencimento).days
        
        # Multa
        if conta['percentual_multa'] > 0:
            valor_multa = float((Decimal(str(conta['valor_total'])) * Decimal(str(conta['percentual_multa']))) / 100)
        
        # Juros
        if conta['percentual_juros'] > 0:
            valor_juros = float((Decimal(str(conta['valor_total'])) * Decimal(str(conta['percentual_juros'])) * dias_atraso) / 100)
    
    valor_total = float(conta['valor_total']) + valor_juros + valor_multa
    
    return jsonify({
        'dias_atraso': dias_atraso,
        'valor_juros': valor_juros,
        'valor_multa': valor_multa,
        'valor_total': valor_total
    })
