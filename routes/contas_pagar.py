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
from utils.auditoria import auditar_agora

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
        return f(*args, **kwargs)
    return decorated_function

@contas_pagar_bp.route('/')
@login_required
@login_required
def lista():
    # Filtros
    fornecedor_id = request.args.get('fornecedor_id', type=int)
    filial_id = request.args.get('filial_id', type=int)
    centro_custo_id = request.args.get('centro_custo_id', type=int)
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
        centro_custo_id=centro_custo_id,
        status=status,
        data_inicio=data_inicio_obj,
        data_fim=data_fim_obj
    )
    
    # Buscar dados para filtros
    fornecedores = FornecedorModel.get_all()
    filiais = FilialModel.get_all()
    centros_custos = CentroCustoModel.get_all()
    
    # Totalizadores
    totalizadores = ContaPagarModel.get_totalizadores({
        'fornecedor_id': fornecedor_id,
        'filial_id': filial_id,
        'centro_custo_id': centro_custo_id
    })
    
    return render_template('contas_pagar/lista.html', 
                         contas=contas,
                         fornecedores=fornecedores,
                         filiais=filiais,
                         centros_custos=centros_custos,
                         totalizadores=totalizadores,
                         filtros={
                             'fornecedor_id': fornecedor_id,
                             'filial_id': filial_id,
                             'centro_custo_id': centro_custo_id,
                             'status': status,
                             'data_inicio': data_inicio,
                             'data_fim': data_fim
                         })

@contas_pagar_bp.route('/nova', methods=['GET', 'POST'])
@login_required
@login_required
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
            'referencia': request.form.get('referencia'),
            'percentual_juros': request.form.get('percentual_juros', 0),
            'percentual_multa': request.form.get('percentual_multa', 0),
            'created_by': session.get('user_id')
        }
        
        resultado = ContaPagarModel.create(dados)
        
        if resultado['success']:
            # Auditoria
            conta_id = resultado.get('id', 0)
            auditar_agora('contas_pagar', conta_id, 'insert', dados)
            
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
@login_required
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
                # Auditoria
                auditar_agora('contas_pagar', conta_id, 'update', {
                    'acao': 'baixa_pagamento',
                    'conta_bancaria_id': dados_baixa['conta_bancaria_id'],
                    'data_pagamento': dados_baixa['data_pagamento'],
                    'valor_pago': str(resultado['valor_pago']),
                    'valor_desconto': dados_baixa['valor_desconto']
                })
                
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
@login_required
def cancelar(conta_id):
    resultado = ContaPagarModel.cancelar(conta_id)
    
    if resultado.get('success'):
        # Auditoria
        auditar_agora('contas_pagar', conta_id, 'update', {
            'acao': 'cancelamento',
            'motivo': 'cancelamento_usuario'
        })
    
    return jsonify(resultado)

@contas_pagar_bp.route('/detalhes/<int:conta_id>')
@login_required
@login_required
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

@contas_pagar_bp.route('/editar/<int:conta_id>', methods=['GET', 'POST'])
@login_required
def editar(conta_id):
    """Edita uma conta a pagar existente"""
    conta = ContaPagarModel.get_by_id(conta_id)
    
    if not conta:
        flash('Conta não encontrada', 'error')
        return redirect(url_for('contas_pagar.lista'))
    
    if conta['status'] == 'pago':
        flash('Não é possível editar uma conta já paga', 'error')
        return redirect(url_for('contas_pagar.lista'))
    
    if request.method == 'POST':
        try:
            dados = {
                'fornecedor_id': int(request.form['fornecedor_id']),
                'tipo_servico_id': int(request.form['tipo_servico_id']) if request.form.get('tipo_servico_id') else None,
                'centro_custo_id': int(request.form['centro_custo_id']) if request.form.get('centro_custo_id') else None,
                'conta_contabil_id': int(request.form['conta_contabil_id']) if request.form.get('conta_contabil_id') else None,
                'filial_id': int(request.form['filial_id']) if request.form.get('filial_id') else None,
                'descricao': request.form['descricao'],
                'numero_documento': request.form.get('numero_documento'),
                'observacoes': request.form.get('observacoes'),
                'valor_total': converter_valor_brasileiro(request.form['valor_total']),
                'data_emissao': request.form['data_emissao'],
                'data_vencimento': request.form['data_vencimento'],
                'referencia': request.form.get('referencia'),
                'percentual_juros': float(request.form.get('percentual_juros', 0)),
                'percentual_multa': float(request.form.get('percentual_multa', 0))
            }
            
            resultado = ContaPagarModel.update(conta_id, dados)
            
            if resultado['success']:
                # Auditoria
                auditar_agora('contas_pagar', conta_id, 'update')
                flash('Conta atualizada com sucesso!', 'success')
                return redirect(url_for('contas_pagar.lista'))
            else:
                flash(resultado['message'], 'error')
        
        except Exception as e:
            flash(f'Erro ao atualizar conta: {str(e)}', 'error')
    
    # GET - Buscar dados para os selects
    fornecedores = FornecedorModel.get_all()
    tipos_servicos = TipoServicoModel.get_all()
    centros_custos = CentroCustoModel.get_all()
    plano_contas = PlanoContaModel.get_analiticas(tipo='despesa')
    filiais = FilialModel.get_all()
    
    return render_template('contas_pagar/form.html', 
                         conta=conta,
                         fornecedores=fornecedores,
                         tipos_servicos=tipos_servicos,
                         centros_custos=centros_custos,
                         contas_analiticas=plano_contas,
                         filiais=filiais)

@contas_pagar_bp.route('/deletar/<int:conta_id>', methods=['POST'])
@login_required
def deletar(conta_id):
    """Exclui (soft delete) uma conta a pagar"""
    resultado = ContaPagarModel.delete(conta_id)
    
    if resultado['success']:
        # Auditoria
        auditar_agora('contas_pagar', conta_id, 'delete')
    
    return jsonify(resultado)

@contas_pagar_bp.route('/baixas')
@login_required
def baixas():
    """Lista todas as baixas (pagamentos) realizadas"""
    # Filtros
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    fornecedor_id = request.args.get('fornecedor_id', type=int)
    
    # Buscar baixas
    baixas_list = ContaPagarModel.get_baixas(
        data_inicio=data_inicio,
        data_fim=data_fim,
        fornecedor_id=fornecedor_id
    )
    
    # Buscar fornecedores para filtro
    fornecedores = FornecedorModel.get_all()
    
    # Calcular total
    total_pago = sum(b['valor_pago'] for b in baixas_list if b['valor_pago'])
    
    return render_template('contas_pagar/baixas.html',
                         baixas=baixas_list,
                         fornecedores=fornecedores,
                         total_pago=total_pago,
                         filtros={
                             'data_inicio': data_inicio,
                             'data_fim': data_fim,
                             'fornecedor_id': fornecedor_id
                         })

@contas_pagar_bp.route('/estornar/<int:conta_id>', methods=['POST'])
@login_required
def estornar(conta_id):
    """Estorna um pagamento realizado"""
    motivo = request.form.get('motivo', 'Sem motivo informado')
    
    resultado = ContaPagarModel.estornar_pagamento(conta_id, motivo)
    
    if resultado['success']:
        # Auditoria
        auditar_agora('contas_pagar', conta_id, 'estorno', dados={'motivo': motivo})
        flash(resultado['message'], 'success')
    else:
        flash(resultado['message'], 'error')
    
    return redirect(url_for('contas_pagar.baixas'))

@contas_pagar_bp.route('/baixas-do-dia')
@login_required
def baixas_do_dia():
    """Relatório de pagamentos do dia atual"""
    from datetime import date
    
    hoje = date.today()
    
    # Buscar baixas do dia
    baixas_list = ContaPagarModel.get_baixas(
        data_inicio=hoje,
        data_fim=hoje
    )
    
    # Calcular total
    total_pago = sum(b['valor_pago'] for b in baixas_list if b['valor_pago'])
    
    return render_template('contas_pagar/baixas_dia.html',
                         baixas=baixas_list,
                         total_pago=total_pago,
                         data=hoje)


@contas_pagar_bp.route('/exportar/pdf')
@login_required
def exportar_pdf():
    """Exporta relatório para PDF"""
    from flask import send_file
    from services.exportacao import ExportacaoService
    
    # Obter filtros da requisição
    filtros = {
        'status': request.args.get('status'),
        'fornecedor_id': request.args.get('fornecedor_id'),
        'filial_id': request.args.get('filial_id'),
        'centro_custo_id': request.args.get('centro_custo_id'),
        'data_inicio': request.args.get('data_inicio'),
        'data_fim': request.args.get('data_fim'),
    }
    
    # Buscar contas com filtros aplicados
    contas = ContaPagarModel.get_all(
        status=filtros.get('status'),
        fornecedor_id=int(filtros['fornecedor_id']) if filtros.get('fornecedor_id') else None,
        filial_id=int(filtros['filial_id']) if filtros.get('filial_id') else None,
        centro_custo_id=int(filtros['centro_custo_id']) if filtros.get('centro_custo_id') else None,
        data_inicio=filtros.get('data_inicio'),
        data_fim=filtros.get('data_fim')
    )
    
    # Gerar PDF
    pdf_buffer = ExportacaoService.exportar_contas_pagar_pdf(contas, filtros)
    
    # Nome do arquivo
    filename = f"contas_pagar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )


@contas_pagar_bp.route('/exportar/excel')
@login_required
def exportar_excel():
    """Exporta relatório para Excel"""
    from flask import send_file
    from services.exportacao import ExportacaoService
    
    # Obter filtros da requisição
    filtros = {
        'status': request.args.get('status'),
        'fornecedor_id': request.args.get('fornecedor_id'),
        'filial_id': request.args.get('filial_id'),
        'centro_custo_id': request.args.get('centro_custo_id'),
        'data_inicio': request.args.get('data_inicio'),
        'data_fim': request.args.get('data_fim'),
    }
    
    # Buscar contas com filtros aplicados
    contas = ContaPagarModel.get_all(
        status=filtros.get('status'),
        fornecedor_id=int(filtros['fornecedor_id']) if filtros.get('fornecedor_id') else None,
        filial_id=int(filtros['filial_id']) if filtros.get('filial_id') else None,
        centro_custo_id=int(filtros['centro_custo_id']) if filtros.get('centro_custo_id') else None,
        data_inicio=filtros.get('data_inicio'),
        data_fim=filtros.get('data_fim')
    )
    
    # Gerar Excel
    excel_buffer = ExportacaoService.exportar_contas_pagar_excel(contas, filtros)
    
    # Nome do arquivo
    filename = f"contas_pagar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    return send_file(
        excel_buffer,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )
