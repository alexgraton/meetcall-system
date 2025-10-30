#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para popular o Plano de Contas com estrutura completa de DRE
Estrutura: 4 níveis hierárquicos
"""

from app import app
from models.plano_conta import PlanoContaModel

def popular():
    """Popula o plano de contas com estrutura DRE"""
    
    contas = [
        # ========================================
        # NÍVEL 1: RECEITAS
        # ========================================
        {
            'codigo': '1',
            'descricao': 'RECEITAS',
            'tipo': 'receita',
            'dre_grupo': None,
            'ordem': 1
        },
        
        # NÍVEL 2: Subgrupos de Receitas
        {
            'codigo': '1.1',
            'descricao': 'Receita Bruta de Vendas e Serviços',
            'tipo': 'receita',
            'dre_grupo': 'receita_bruta',
            'ordem': 1
        },
        {
            'codigo': '1.2',
            'descricao': 'Deduções da Receita Bruta',
            'tipo': 'receita',
            'dre_grupo': 'deducoes',
            'ordem': 2
        },
        {
            'codigo': '1.3',
            'descricao': 'Outras Receitas Operacionais',
            'tipo': 'receita',
            'dre_grupo': 'receita_liquida',
            'ordem': 3
        },
        
        # NÍVEL 3: Categorias de Receita Bruta
        {
            'codigo': '1.1.01',
            'descricao': 'Receita de Serviços',
            'tipo': 'receita',
            'dre_grupo': 'receita_bruta',
            'ordem': 1
        },
        {
            'codigo': '1.1.02',
            'descricao': 'Receita de Produtos',
            'tipo': 'receita',
            'dre_grupo': 'receita_bruta',
            'ordem': 2
        },
        {
            'codigo': '1.1.03',
            'descricao': 'Receita de Revenda',
            'tipo': 'receita',
            'dre_grupo': 'receita_bruta',
            'ordem': 3
        },
        
        # NÍVEL 4: Detalhamento de Receita de Serviços
        {
            'codigo': '1.1.01.001',
            'descricao': 'Serviços de Consultoria',
            'tipo': 'receita',
            'dre_grupo': 'receita_bruta',
            'ordem': 1
        },
        {
            'codigo': '1.1.01.002',
            'descricao': 'Serviços de Implementação',
            'tipo': 'receita',
            'dre_grupo': 'receita_bruta',
            'ordem': 2
        },
        {
            'codigo': '1.1.01.003',
            'descricao': 'Serviços de Suporte',
            'tipo': 'receita',
            'dre_grupo': 'receita_bruta',
            'ordem': 3
        },
        {
            'codigo': '1.1.01.004',
            'descricao': 'Mensalidades/Assinaturas',
            'tipo': 'receita',
            'dre_grupo': 'receita_bruta',
            'ordem': 4
        },
        
        # NÍVEL 3: Categorias de Deduções
        {
            'codigo': '1.2.01',
            'descricao': 'Impostos sobre Vendas',
            'tipo': 'receita',
            'dre_grupo': 'deducoes',
            'ordem': 1
        },
        {
            'codigo': '1.2.02',
            'descricao': 'Devoluções e Cancelamentos',
            'tipo': 'receita',
            'dre_grupo': 'deducoes',
            'ordem': 2
        },
        {
            'codigo': '1.2.03',
            'descricao': 'Descontos Concedidos',
            'tipo': 'receita',
            'dre_grupo': 'deducoes',
            'ordem': 3
        },
        
        # NÍVEL 4: Detalhamento de Impostos
        {
            'codigo': '1.2.01.001',
            'descricao': 'ISS',
            'tipo': 'receita',
            'dre_grupo': 'deducoes',
            'ordem': 1
        },
        {
            'codigo': '1.2.01.002',
            'descricao': 'PIS',
            'tipo': 'receita',
            'dre_grupo': 'deducoes',
            'ordem': 2
        },
        {
            'codigo': '1.2.01.003',
            'descricao': 'COFINS',
            'tipo': 'receita',
            'dre_grupo': 'deducoes',
            'ordem': 3
        },
        {
            'codigo': '1.2.01.004',
            'descricao': 'CSLL',
            'tipo': 'receita',
            'dre_grupo': 'deducoes',
            'ordem': 4
        },
        {
            'codigo': '1.2.01.005',
            'descricao': 'IRPJ',
            'tipo': 'receita',
            'dre_grupo': 'deducoes',
            'ordem': 5
        },
        
        # ========================================
        # NÍVEL 1: DESPESAS
        # ========================================
        {
            'codigo': '2',
            'descricao': 'DESPESAS',
            'tipo': 'despesa',
            'dre_grupo': None,
            'ordem': 2
        },
        
        # NÍVEL 2: Subgrupos de Despesas
        {
            'codigo': '2.1',
            'descricao': 'Custo dos Serviços Prestados',
            'tipo': 'despesa',
            'dre_grupo': 'custo_servicos',
            'ordem': 1
        },
        {
            'codigo': '2.2',
            'descricao': 'Despesas Operacionais',
            'tipo': 'despesa',
            'dre_grupo': 'despesas_operacionais',
            'ordem': 2
        },
        {
            'codigo': '2.3',
            'descricao': 'Despesas Financeiras',
            'tipo': 'despesa',
            'dre_grupo': 'resultado',
            'ordem': 3
        },
        
        # NÍVEL 3: Categorias de Custos
        {
            'codigo': '2.1.01',
            'descricao': 'Mão de Obra Direta',
            'tipo': 'despesa',
            'dre_grupo': 'custo_servicos',
            'ordem': 1
        },
        {
            'codigo': '2.1.02',
            'descricao': 'Custos com Terceiros',
            'tipo': 'despesa',
            'dre_grupo': 'custo_servicos',
            'ordem': 2
        },
        {
            'codigo': '2.1.03',
            'descricao': 'Materiais e Insumos',
            'tipo': 'despesa',
            'dre_grupo': 'custo_servicos',
            'ordem': 3
        },
        
        # NÍVEL 4: Detalhamento de Mão de Obra
        {
            'codigo': '2.1.01.001',
            'descricao': 'Salários - Equipe Técnica',
            'tipo': 'despesa',
            'dre_grupo': 'custo_servicos',
            'ordem': 1
        },
        {
            'codigo': '2.1.01.002',
            'descricao': 'Encargos Sociais - Equipe Técnica',
            'tipo': 'despesa',
            'dre_grupo': 'custo_servicos',
            'ordem': 2
        },
        {
            'codigo': '2.1.01.003',
            'descricao': 'Benefícios - Equipe Técnica',
            'tipo': 'despesa',
            'dre_grupo': 'custo_servicos',
            'ordem': 3
        },
        
        # NÍVEL 3: Despesas Administrativas
        {
            'codigo': '2.2.01',
            'descricao': 'Despesas com Pessoal',
            'tipo': 'despesa',
            'dre_grupo': 'despesas_operacionais',
            'ordem': 1
        },
        {
            'codigo': '2.2.02',
            'descricao': 'Despesas Gerais',
            'tipo': 'despesa',
            'dre_grupo': 'despesas_operacionais',
            'ordem': 2
        },
        {
            'codigo': '2.2.03',
            'descricao': 'Despesas com Vendas',
            'tipo': 'despesa',
            'dre_grupo': 'despesas_operacionais',
            'ordem': 3
        },
        {
            'codigo': '2.2.04',
            'descricao': 'Despesas de TI',
            'tipo': 'despesa',
            'dre_grupo': 'despesas_operacionais',
            'ordem': 4
        },
        {
            'codigo': '2.2.05',
            'descricao': 'Despesas com Marketing',
            'tipo': 'despesa',
            'dre_grupo': 'despesas_operacionais',
            'ordem': 5
        },
        
        # NÍVEL 4: Detalhamento Despesas com Pessoal
        {
            'codigo': '2.2.01.001',
            'descricao': 'Salários - Administrativo',
            'tipo': 'despesa',
            'dre_grupo': 'despesas_operacionais',
            'ordem': 1
        },
        {
            'codigo': '2.2.01.002',
            'descricao': 'Encargos Sociais - Administrativo',
            'tipo': 'despesa',
            'dre_grupo': 'despesas_operacionais',
            'ordem': 2
        },
        {
            'codigo': '2.2.01.003',
            'descricao': 'Benefícios - Administrativo',
            'tipo': 'despesa',
            'dre_grupo': 'despesas_operacionais',
            'ordem': 3
        },
        {
            'codigo': '2.2.01.004',
            'descricao': 'Treinamentos e Capacitação',
            'tipo': 'despesa',
            'dre_grupo': 'despesas_operacionais',
            'ordem': 4
        },
        
        # NÍVEL 4: Detalhamento Despesas Gerais
        {
            'codigo': '2.2.02.001',
            'descricao': 'Aluguel',
            'tipo': 'despesa',
            'dre_grupo': 'despesas_operacionais',
            'ordem': 1
        },
        {
            'codigo': '2.2.02.002',
            'descricao': 'Energia Elétrica',
            'tipo': 'despesa',
            'dre_grupo': 'despesas_operacionais',
            'ordem': 2
        },
        {
            'codigo': '2.2.02.003',
            'descricao': 'Água e Esgoto',
            'tipo': 'despesa',
            'dre_grupo': 'despesas_operacionais',
            'ordem': 3
        },
        {
            'codigo': '2.2.02.004',
            'descricao': 'Telefone e Internet',
            'tipo': 'despesa',
            'dre_grupo': 'despesas_operacionais',
            'ordem': 4
        },
        {
            'codigo': '2.2.02.005',
            'descricao': 'Material de Escritório',
            'tipo': 'despesa',
            'dre_grupo': 'despesas_operacionais',
            'ordem': 5
        },
        {
            'codigo': '2.2.02.006',
            'descricao': 'Limpeza e Conservação',
            'tipo': 'despesa',
            'dre_grupo': 'despesas_operacionais',
            'ordem': 6
        },
        {
            'codigo': '2.2.02.007',
            'descricao': 'Segurança',
            'tipo': 'despesa',
            'dre_grupo': 'despesas_operacionais',
            'ordem': 7
        },
        {
            'codigo': '2.2.02.008',
            'descricao': 'Condomínio',
            'tipo': 'despesa',
            'dre_grupo': 'despesas_operacionais',
            'ordem': 8
        },
        
        # NÍVEL 4: Detalhamento Despesas TI
        {
            'codigo': '2.2.04.001',
            'descricao': 'Licenças de Software',
            'tipo': 'despesa',
            'dre_grupo': 'despesas_operacionais',
            'ordem': 1
        },
        {
            'codigo': '2.2.04.002',
            'descricao': 'Hospedagem e Cloud',
            'tipo': 'despesa',
            'dre_grupo': 'despesas_operacionais',
            'ordem': 2
        },
        {
            'codigo': '2.2.04.003',
            'descricao': 'Manutenção de Equipamentos',
            'tipo': 'despesa',
            'dre_grupo': 'despesas_operacionais',
            'ordem': 3
        },
        {
            'codigo': '2.2.04.004',
            'descricao': 'Suporte Técnico',
            'tipo': 'despesa',
            'dre_grupo': 'despesas_operacionais',
            'ordem': 4
        },
        
        # NÍVEL 4: Detalhamento Despesas Marketing
        {
            'codigo': '2.2.05.001',
            'descricao': 'Publicidade Online',
            'tipo': 'despesa',
            'dre_grupo': 'despesas_operacionais',
            'ordem': 1
        },
        {
            'codigo': '2.2.05.002',
            'descricao': 'Publicidade Offline',
            'tipo': 'despesa',
            'dre_grupo': 'despesas_operacionais',
            'ordem': 2
        },
        {
            'codigo': '2.2.05.003',
            'descricao': 'Eventos e Patrocínios',
            'tipo': 'despesa',
            'dre_grupo': 'despesas_operacionais',
            'ordem': 3
        },
        {
            'codigo': '2.2.05.004',
            'descricao': 'Material Promocional',
            'tipo': 'despesa',
            'dre_grupo': 'despesas_operacionais',
            'ordem': 4
        },
        
        # NÍVEL 3: Despesas Financeiras
        {
            'codigo': '2.3.01',
            'descricao': 'Juros Passivos',
            'tipo': 'despesa',
            'dre_grupo': 'resultado',
            'ordem': 1
        },
        {
            'codigo': '2.3.02',
            'descricao': 'Tarifas Bancárias',
            'tipo': 'despesa',
            'dre_grupo': 'resultado',
            'ordem': 2
        },
        {
            'codigo': '2.3.03',
            'descricao': 'IOF',
            'tipo': 'despesa',
            'dre_grupo': 'resultado',
            'ordem': 3
        },
        
        # NÍVEL 4: Detalhamento Despesas Financeiras
        {
            'codigo': '2.3.01.001',
            'descricao': 'Juros de Empréstimos',
            'tipo': 'despesa',
            'dre_grupo': 'resultado',
            'ordem': 1
        },
        {
            'codigo': '2.3.01.002',
            'descricao': 'Juros de Financiamentos',
            'tipo': 'despesa',
            'dre_grupo': 'resultado',
            'ordem': 2
        },
        {
            'codigo': '2.3.01.003',
            'descricao': 'Juros de Cartão de Crédito',
            'tipo': 'despesa',
            'dre_grupo': 'resultado',
            'ordem': 3
        },
        
        # ========================================
        # NÍVEL 1: ATIVO
        # ========================================
        {
            'codigo': '3',
            'descricao': 'ATIVO',
            'tipo': 'ativo',
            'dre_grupo': None,
            'ordem': 3
        },
        
        # NÍVEL 2: Ativo Circulante
        {
            'codigo': '3.1',
            'descricao': 'Ativo Circulante',
            'tipo': 'ativo',
            'dre_grupo': None,
            'ordem': 1
        },
        {
            'codigo': '3.2',
            'descricao': 'Ativo Não Circulante',
            'tipo': 'ativo',
            'dre_grupo': None,
            'ordem': 2
        },
        
        # NÍVEL 3: Categorias Ativo Circulante
        {
            'codigo': '3.1.01',
            'descricao': 'Disponibilidades',
            'tipo': 'ativo',
            'dre_grupo': None,
            'ordem': 1
        },
        {
            'codigo': '3.1.02',
            'descricao': 'Contas a Receber',
            'tipo': 'ativo',
            'dre_grupo': None,
            'ordem': 2
        },
        {
            'codigo': '3.1.03',
            'descricao': 'Estoques',
            'tipo': 'ativo',
            'dre_grupo': None,
            'ordem': 3
        },
        
        # NÍVEL 4: Detalhamento Disponibilidades
        {
            'codigo': '3.1.01.001',
            'descricao': 'Caixa',
            'tipo': 'ativo',
            'dre_grupo': None,
            'ordem': 1
        },
        {
            'codigo': '3.1.01.002',
            'descricao': 'Banco - Conta Corrente',
            'tipo': 'ativo',
            'dre_grupo': None,
            'ordem': 2
        },
        {
            'codigo': '3.1.01.003',
            'descricao': 'Banco - Conta Poupança',
            'tipo': 'ativo',
            'dre_grupo': None,
            'ordem': 3
        },
        {
            'codigo': '3.1.01.004',
            'descricao': 'Aplicações Financeiras',
            'tipo': 'ativo',
            'dre_grupo': None,
            'ordem': 4
        },
        
        # NÍVEL 3: Categorias Ativo Não Circulante
        {
            'codigo': '3.2.01',
            'descricao': 'Imobilizado',
            'tipo': 'ativo',
            'dre_grupo': None,
            'ordem': 1
        },
        {
            'codigo': '3.2.02',
            'descricao': 'Intangível',
            'tipo': 'ativo',
            'dre_grupo': None,
            'ordem': 2
        },
        
        # NÍVEL 4: Detalhamento Imobilizado
        {
            'codigo': '3.2.01.001',
            'descricao': 'Móveis e Utensílios',
            'tipo': 'ativo',
            'dre_grupo': None,
            'ordem': 1
        },
        {
            'codigo': '3.2.01.002',
            'descricao': 'Equipamentos de Informática',
            'tipo': 'ativo',
            'dre_grupo': None,
            'ordem': 2
        },
        {
            'codigo': '3.2.01.003',
            'descricao': 'Veículos',
            'tipo': 'ativo',
            'dre_grupo': None,
            'ordem': 3
        },
        
        # ========================================
        # NÍVEL 1: PASSIVO
        # ========================================
        {
            'codigo': '4',
            'descricao': 'PASSIVO',
            'tipo': 'passivo',
            'dre_grupo': None,
            'ordem': 4
        },
        
        # NÍVEL 2: Passivo Circulante
        {
            'codigo': '4.1',
            'descricao': 'Passivo Circulante',
            'tipo': 'passivo',
            'dre_grupo': None,
            'ordem': 1
        },
        {
            'codigo': '4.2',
            'descricao': 'Passivo Não Circulante',
            'tipo': 'passivo',
            'dre_grupo': None,
            'ordem': 2
        },
        
        # NÍVEL 3: Categorias Passivo Circulante
        {
            'codigo': '4.1.01',
            'descricao': 'Fornecedores',
            'tipo': 'passivo',
            'dre_grupo': None,
            'ordem': 1
        },
        {
            'codigo': '4.1.02',
            'descricao': 'Obrigações Fiscais',
            'tipo': 'passivo',
            'dre_grupo': None,
            'ordem': 2
        },
        {
            'codigo': '4.1.03',
            'descricao': 'Obrigações Trabalhistas',
            'tipo': 'passivo',
            'dre_grupo': None,
            'ordem': 3
        },
        {
            'codigo': '4.1.04',
            'descricao': 'Empréstimos e Financiamentos',
            'tipo': 'passivo',
            'dre_grupo': None,
            'ordem': 4
        },
        
        # NÍVEL 4: Detalhamento Obrigações
        {
            'codigo': '4.1.01.001',
            'descricao': 'Fornecedores Nacionais',
            'tipo': 'passivo',
            'dre_grupo': None,
            'ordem': 1
        },
        {
            'codigo': '4.1.02.001',
            'descricao': 'INSS a Recolher',
            'tipo': 'passivo',
            'dre_grupo': None,
            'ordem': 1
        },
        {
            'codigo': '4.1.02.002',
            'descricao': 'FGTS a Recolher',
            'tipo': 'passivo',
            'dre_grupo': None,
            'ordem': 2
        },
        {
            'codigo': '4.1.02.003',
            'descricao': 'ISS a Recolher',
            'tipo': 'passivo',
            'dre_grupo': None,
            'ordem': 3
        },
        
        # ========================================
        # NÍVEL 1: PATRIMÔNIO LÍQUIDO
        # ========================================
        {
            'codigo': '5',
            'descricao': 'PATRIMÔNIO LÍQUIDO',
            'tipo': 'patrimonio',
            'dre_grupo': None,
            'ordem': 5
        },
        
        # NÍVEL 2: Componentes do PL
        {
            'codigo': '5.1',
            'descricao': 'Capital Social',
            'tipo': 'patrimonio',
            'dre_grupo': None,
            'ordem': 1
        },
        {
            'codigo': '5.2',
            'descricao': 'Reservas',
            'tipo': 'patrimonio',
            'dre_grupo': None,
            'ordem': 2
        },
        {
            'codigo': '5.3',
            'descricao': 'Lucros/Prejuízos Acumulados',
            'tipo': 'patrimonio',
            'dre_grupo': None,
            'ordem': 3
        },
        
        # NÍVEL 3: Detalhamento
        {
            'codigo': '5.1.01',
            'descricao': 'Capital Subscrito',
            'tipo': 'patrimonio',
            'dre_grupo': None,
            'ordem': 1
        },
        {
            'codigo': '5.1.02',
            'descricao': 'Capital Integralizado',
            'tipo': 'patrimonio',
            'dre_grupo': None,
            'ordem': 2
        },
        
        # NÍVEL 4: Contas Analíticas
        {
            'codigo': '5.1.01.001',
            'descricao': 'Capital Social - Sócio 1',
            'tipo': 'patrimonio',
            'dre_grupo': None,
            'ordem': 1
        },
        {
            'codigo': '5.1.01.002',
            'descricao': 'Capital Social - Sócio 2',
            'tipo': 'patrimonio',
            'dre_grupo': None,
            'ordem': 2
        },
    ]
    
    print("Iniciando população do Plano de Contas...")
    print(f"Total de contas a criar: {len(contas)}\n")
    
    sucesso = 0
    erros = 0
    
    for conta in contas:
        resultado = PlanoContaModel.create(conta)
        
        if resultado['success']:
            sucesso += 1
            nivel = conta['codigo'].count('.') + 1
            indent = '  ' * (nivel - 1)
            print(f"✓ {indent}{conta['codigo']} - {conta['descricao']}")
        else:
            erros += 1
            print(f"✗ ERRO ao criar {conta['codigo']}: {resultado['message']}")
    
    print(f"\n{'='*60}")
    print(f"População concluída!")
    print(f"Sucesso: {sucesso} contas")
    print(f"Erros: {erros} contas")
    print(f"{'='*60}")

if __name__ == '__main__':
    with app.app_context():
        popular()
