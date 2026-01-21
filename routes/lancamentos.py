"""
Rotas para gerenciamento de Lancamentos Manuais
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from datetime import datetime, date
from decimal import Decimal
from models.lancamento_manual import LancamentoManualModel
from models.filial import FilialModel
from models.tipo_servico import TipoServicoModel
from models.centro_custo import CentroCustoModel
from models.plano_conta import PlanoContaModel
from models.fornecedor import FornecedorModel
from models.cliente import ClienteModel

lancamentos_bp = Blueprint('lancamentos', __name__, url_prefix='/lancamentos')

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

@lancamentos_bp.route('/')
@login_required
@login_required
def lista():
    tipo = request.args.get('tipo')
    filial_id = request.args.get('filial_id', type=int)
    forma_pagamento = request.args.get('forma_pagamento')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    
    data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date() if data_inicio else None
    data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date() if data_fim else None
    
    lancamentos = LancamentoManualModel.get_all(
        tipo=tipo,
        filial_id=filial_id,
        data_inicio=data_inicio_obj,
        data_fim=data_fim_obj,
        forma_pagamento=forma_pagamento
    )
    
    filiais = FilialModel.get_all()
    totalizadores = LancamentoManualModel.get_totalizadores(data_inicio_obj, data_fim_obj, filial_id)
    
    return render_template('lancamentos/lista.html',
                         lancamentos=lancamentos,
                         filiais=filiais,
                         totalizadores=totalizadores,
                         filtros={
                             'tipo': tipo,
                             'filial_id': filial_id,
                             'forma_pagamento': forma_pagamento,
                             'data_inicio': data_inicio,
                             'data_fim': data_fim
                         })

@lancamentos_bp.route('/novo', methods=['GET', 'POST'])
@login_required
@login_required
def novo():
    if request.method == 'POST':
        try:
            dados = {
                'tipo': request.form['tipo'],
                'descricao': request.form['descricao'],
                'valor': Decimal(request.form['valor']),
                'data_lancamento': datetime.strptime(request.form['data_lancamento'], '%Y-%m-%d').date(),
                'data_competencia': datetime.strptime(request.form['data_competencia'], '%Y-%m-%d').date() if request.form.get('data_competencia') else None,
                'filial_id': int(request.form['filial_id']) if request.form.get('filial_id') else None,
                'tipo_servico_id': int(request.form['tipo_servico_id']) if request.form.get('tipo_servico_id') else None,
                'centro_custo_id': int(request.form['centro_custo_id']) if request.form.get('centro_custo_id') else None,
                'conta_contabil_id': int(request.form['conta_contabil_id']) if request.form.get('conta_contabil_id') else None,
                'fornecedor_id': int(request.form['fornecedor_id']) if request.form.get('fornecedor_id') else None,
                'cliente_id': int(request.form['cliente_id']) if request.form.get('cliente_id') else None,
                'numero_documento': request.form.get('numero_documento'),
                'forma_pagamento': request.form.get('forma_pagamento'),
                'observacoes': request.form.get('observacoes'),
                'created_by': session.get('user_id')
            }
            
            LancamentoManualModel.create(dados)
            flash(f'Lançamento de {dados["tipo"]} criado com sucesso!', 'success')
            return redirect(url_for('lancamentos.lista'))
            
        except Exception as e:
            flash(f'Erro ao criar lançamento: {str(e)}', 'error')
    
    filiais = FilialModel.get_all()
    tipos_servicos = TipoServicoModel.get_all()
    centros_custos = CentroCustoModel.get_all()
    plano_contas = PlanoContaModel.get_all()
    fornecedores = FornecedorModel.get_all()
    clientes = ClienteModel.get_all()
    
    return render_template('lancamentos/form.html',
                         filiais=filiais,
                         tipos_servicos=tipos_servicos,
                         centros_custos=centros_custos,
                         plano_contas=plano_contas,
                         fornecedores=fornecedores,
                         clientes=clientes,
                         lancamento=None,
                         today=date.today().strftime('%Y-%m-%d'))

@lancamentos_bp.route('/<int:lancamento_id>/editar', methods=['GET', 'POST'])
@login_required
@login_required
def editar(lancamento_id):
    lancamento = LancamentoManualModel.get_by_id(lancamento_id)
    
    if not lancamento:
        flash('Lançamento não encontrado.', 'error')
        return redirect(url_for('lancamentos.lista'))
    
    if request.method == 'POST':
        try:
            dados = {
                'tipo': request.form['tipo'],
                'descricao': request.form['descricao'],
                'valor': Decimal(request.form['valor']),
                'data_lancamento': datetime.strptime(request.form['data_lancamento'], '%Y-%m-%d').date(),
                'data_competencia': datetime.strptime(request.form['data_competencia'], '%Y-%m-%d').date() if request.form.get('data_competencia') else None,
                'filial_id': int(request.form['filial_id']) if request.form.get('filial_id') else None,
                'tipo_servico_id': int(request.form['tipo_servico_id']) if request.form.get('tipo_servico_id') else None,
                'centro_custo_id': int(request.form['centro_custo_id']) if request.form.get('centro_custo_id') else None,
                'conta_contabil_id': int(request.form['conta_contabil_id']) if request.form.get('conta_contabil_id') else None,
                'fornecedor_id': int(request.form['fornecedor_id']) if request.form.get('fornecedor_id') else None,
                'cliente_id': int(request.form['cliente_id']) if request.form.get('cliente_id') else None,
                'numero_documento': request.form.get('numero_documento'),
                'forma_pagamento': request.form.get('forma_pagamento'),
                'observacoes': request.form.get('observacoes')
            }
            
            LancamentoManualModel.update(lancamento_id, dados)
            flash('Lançamento atualizado com sucesso!', 'success')
            return redirect(url_for('lancamentos.lista'))
            
        except Exception as e:
            flash(f'Erro ao atualizar lançamento: {str(e)}', 'error')
    
    filiais = FilialModel.get_all()
    tipos_servicos = TipoServicoModel.get_all()
    centros_custos = CentroCustoModel.get_all()
    plano_contas = PlanoContaModel.get_all()
    fornecedores = FornecedorModel.get_all()
    clientes = ClienteModel.get_all()
    
    return render_template('lancamentos/form.html',
                         filiais=filiais,
                         tipos_servicos=tipos_servicos,
                         centros_custos=centros_custos,
                         plano_contas=plano_contas,
                         fornecedores=fornecedores,
                         clientes=clientes,
                         lancamento=lancamento,
                         today=date.today().strftime('%Y-%m-%d'))

@lancamentos_bp.route('/<int:lancamento_id>/excluir', methods=['POST'])
@login_required
@login_required
def excluir(lancamento_id):
    try:
        LancamentoManualModel.delete(lancamento_id)
        flash('Lançamento excluído com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao excluir lançamento: {str(e)}', 'error')
    
    return redirect(url_for('lancamentos.lista'))
