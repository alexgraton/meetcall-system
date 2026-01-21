"""
Rotas para Contas Bancárias
Gerencia contas correntes, poupança e caixa
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models.conta_bancaria import ContaBancariaModel
from models.filial import FilialModel
from decimal import Decimal
from utils.auditoria import auditar_agora

contas_bancarias_bp = Blueprint('contas_bancarias', __name__, url_prefix='/contas_bancarias')

@contas_bancarias_bp.route('/')
def lista():
    """Lista todas as contas bancárias com filtros"""
    
    # Capturar filtros
    filtros = {}
    
    if request.args.get('filial_id'):
        filtros['filial_id'] = int(request.args.get('filial_id'))
    
    if request.args.get('tipo_conta'):
        filtros['tipo_conta'] = request.args.get('tipo_conta')
    
    if request.args.get('ativo'):
        filtros['ativo'] = request.args.get('ativo') == '1'
    
    # Buscar contas e totalizadores
    contas = ContaBancariaModel.get_all(filtros)
    totalizadores = ContaBancariaModel.get_totalizadores(
        filial_id=filtros.get('filial_id')
    )
    
    # Buscar filiais para o filtro
    filiais = FilialModel.get_all()
    
    return render_template(
        'contas_bancarias/lista.html',
        contas=contas,
        totalizadores=totalizadores,
        filiais=filiais,
        filtros=filtros
    )

@contas_bancarias_bp.route('/nova', methods=['GET', 'POST'])
def nova():
    """Cria uma nova conta bancária"""
    
    if request.method == 'POST':
        try:
            dados = {
                'banco': request.form.get('banco'),
                'agencia': request.form.get('agencia'),
                'numero_conta': request.form.get('numero_conta'),
                'tipo_conta': request.form.get('tipo_conta', 'corrente'),
                'descricao': request.form.get('descricao'),
                'saldo_inicial': Decimal(request.form.get('saldo_inicial', '0')),
                'moeda': request.form.get('moeda', 'BRL'),
                'filial_id': int(request.form.get('filial_id')) if request.form.get('filial_id') else None,
                'ativo': 1
            }
            
            conta_id = ContaBancariaModel.create(dados)
            flash(f'Conta bancária criada com sucesso! ID: {conta_id}', 'success')
            return redirect(url_for('contas_bancarias.lista'))
            
        except Exception as e:
            flash(f'Erro ao criar conta bancária: {str(e)}', 'error')
    
    # GET - exibir formulário
    filiais = FilialModel.get_all()
    
    return render_template(
        'contas_bancarias/form.html',
        conta=None,
        filiais=filiais
    )

@contas_bancarias_bp.route('/<int:conta_id>/editar', methods=['GET', 'POST'])
def editar(conta_id):
    """Edita uma conta bancária existente"""
    
    conta = ContaBancariaModel.get_by_id(conta_id)
    
    if not conta:
        flash('Conta bancária não encontrada', 'error')
        return redirect(url_for('contas_bancarias.lista'))
    
    if request.method == 'POST':
        try:
            dados = {
                'banco': request.form.get('banco'),
                'agencia': request.form.get('agencia'),
                'numero_conta': request.form.get('numero_conta'),
                'tipo_conta': request.form.get('tipo_conta'),
                'descricao': request.form.get('descricao'),
                'moeda': request.form.get('moeda'),
                'filial_id': int(request.form.get('filial_id')) if request.form.get('filial_id') else None,
                'ativo': 1 if request.form.get('ativo') else 0
            }
            
            ContaBancariaModel.update(conta_id, dados)
            flash('Conta bancária atualizada com sucesso!', 'success')
            return redirect(url_for('contas_bancarias.detalhes', conta_id=conta_id))
            
        except Exception as e:
            flash(f'Erro ao atualizar conta bancária: {str(e)}', 'error')
    
    # GET - exibir formulário
    filiais = FilialModel.get_all()
    
    return render_template(
        'contas_bancarias/form.html',
        conta=conta,
        filiais=filiais
    )

@contas_bancarias_bp.route('/<int:conta_id>')
def detalhes(conta_id):
    """Exibe detalhes de uma conta bancária"""
    
    conta = ContaBancariaModel.get_by_id(conta_id)
    
    if not conta:
        flash('Conta bancária não encontrada', 'error')
        return redirect(url_for('contas_bancarias.lista'))
    
    return render_template(
        'contas_bancarias/detalhes.html',
        conta=conta
    )

@contas_bancarias_bp.route('/<int:conta_id>/excluir', methods=['POST'])
def excluir(conta_id):
    """Desativa uma conta bancária (soft delete)"""
    
    try:
        ContaBancariaModel.delete(conta_id)
        flash('Conta bancária desativada com sucesso!', 'success')
    except Exception as e:
        flash(f'Erro ao desativar conta bancária: {str(e)}', 'error')
    
    return redirect(url_for('contas_bancarias.lista'))

@contas_bancarias_bp.route('/<int:conta_id>/ajustar_saldo', methods=['POST'])
def ajustar_saldo(conta_id):
    """Ajusta o saldo de uma conta bancária"""
    
    try:
        valor = Decimal(request.form.get('valor', '0'))
        operacao = request.form.get('operacao', 'credito')  # credito ou debito
        descricao = request.form.get('descricao')
        
        resultado = ContaBancariaModel.ajustar_saldo(
            conta_id=conta_id,
            valor=valor,
            operacao=operacao,
            descricao=descricao
        )
        
        if resultado:
            flash(f'Saldo ajustado! Novo saldo: R$ {resultado["saldo_novo"]:,.2f}', 'success')
        else:
            flash('Erro ao ajustar saldo', 'error')
            
    except Exception as e:
        flash(f'Erro: {str(e)}', 'error')
    
    return redirect(url_for('contas_bancarias.detalhes', conta_id=conta_id))
