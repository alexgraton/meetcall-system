"""
Script para enviar alertas de vencimentos e saldo baixo

Uso:
    python enviar_alertas.py --tipo vencimentos --dias 7 --email admin@exemplo.com
    python enviar_alertas.py --tipo saldo --email admin@exemplo.com
    python enviar_alertas.py --tipo todos --email admin@exemplo.com

Configuração:
    Configure as variáveis de ambiente:
    - SMTP_USER: Email SMTP
    - SMTP_PASSWORD: Senha SMTP
    - SMTP_HOST: Servidor SMTP (padrão: smtp.gmail.com)
    - SMTP_PORT: Porta SMTP (padrão: 587)
"""
import os
import sys
import argparse
from utils.notificacoes import Notificacoes


def main():
    parser = argparse.ArgumentParser(description='Enviar alertas financeiros por email')
    parser.add_argument('--tipo', choices=['vencimentos', 'saldo', 'todos'], default='vencimentos',
                        help='Tipo de alerta a enviar')
    parser.add_argument('--dias', type=int, default=7,
                        help='Dias de antecedência para alertas de vencimento (padrão: 7)')
    parser.add_argument('--email', required=True,
                        help='Email do destinatário')
    
    args = parser.parse_args()
    
    # Configurar notificações
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    
    if not smtp_user or not smtp_password:
        print("❌ ERRO: Configure as variáveis de ambiente SMTP_USER e SMTP_PASSWORD")
        print("\nExemplo (.env):")
        print("SMTP_USER=seu-email@gmail.com")
        print("SMTP_PASSWORD=sua-senha-app")
        print("\nPara Gmail, gere uma senha de app em:")
        print("https://myaccount.google.com/apppasswords")
        sys.exit(1)
    
    notif = Notificacoes(
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        smtp_user=smtp_user,
        smtp_password=smtp_password
    )
    
    print(f"📧 Destinatário: {args.email}")
    print(f"🔔 Tipo de alerta: {args.tipo}")
    print("-" * 50)
    
    # Enviar alertas conforme tipo
    if args.tipo in ['vencimentos', 'todos']:
        print(f"\n🔍 Verificando contas vencendo em {args.dias} dias...")
        contas = Notificacoes.verificar_contas_vencendo(args.dias)
        
        total = len(contas['contas_pagar']) + len(contas['contas_receber'])
        
        if total > 0:
            print(f"   ✓ Encontradas {len(contas['contas_pagar'])} contas a pagar")
            print(f"   ✓ Encontradas {len(contas['contas_receber'])} contas a receber")
            
            if notif.enviar_alerta_vencimentos(args.email, args.dias):
                print(f"   ✅ Email de vencimentos enviado com sucesso!")
            else:
                print(f"   ❌ Erro ao enviar email de vencimentos")
        else:
            print(f"   ℹ️  Nenhuma conta vencendo nos próximos {args.dias} dias")
    
    if args.tipo in ['saldo', 'todos']:
        print(f"\n🔍 Verificando saldos baixos...")
        contas_saldo = Notificacoes.verificar_saldo_baixo()
        
        if contas_saldo:
            print(f"   ⚠️  {len(contas_saldo)} conta(s) com saldo abaixo do limite")
            
            # Gerar HTML para saldo baixo
            html = gerar_email_saldo_baixo(contas_saldo)
            assunto = f"⚠️ Alerta: {len(contas_saldo)} conta(s) com saldo baixo"
            
            if notif.enviar_email(args.email, assunto, html):
                print(f"   ✅ Email de saldo baixo enviado com sucesso!")
            else:
                print(f"   ❌ Erro ao enviar email de saldo baixo")
        else:
            print(f"   ℹ️  Todas as contas com saldo adequado")
    
    print("\n" + "=" * 50)
    print("✅ Processamento concluído!")


def gerar_email_saldo_baixo(contas):
    """Gera HTML para email de saldo baixo"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #dc2626; color: white; padding: 20px; text-align: center; }}
            .content {{ background: #f9fafb; padding: 20px; }}
            .alert {{ background: #fee2e2; border-left: 4px solid #dc2626; padding: 15px; margin: 15px 0; }}
            table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
            th {{ background: #e5e7eb; padding: 10px; text-align: left; }}
            td {{ padding: 10px; border-bottom: 1px solid #e5e7eb; }}
            .saldo-baixo {{ color: #dc2626; font-weight: bold; }}
            .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #6b7280; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>⚠️ Alerta de Saldo Baixo</h1>
                <p>MeetCall System - Gestão Financeira</p>
            </div>
            
            <div class="content">
                <p>Olá,</p>
                <p>As seguintes contas bancárias estão com saldo abaixo do limite de alerta:</p>
                
                <div class="alert">
                    <h3>💳 Contas com Saldo Baixo</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>Banco</th>
                                <th>Conta</th>
                                <th>Saldo Atual</th>
                                <th>Limite Alerta</th>
                                <th>% do Limite</th>
                            </tr>
                        </thead>
                        <tbody>
    """
    
    for conta in contas:
        percentual = conta.get('percentual_saldo', 0) or 0
        html += f"""
                            <tr>
                                <td>{conta['banco']}</td>
                                <td>{conta['agencia']}-{conta['conta']} ({conta['nome']})</td>
                                <td class="saldo-baixo">R$ {float(conta['saldo_atual']):,.2f}</td>
                                <td>R$ {float(conta['limite_alerta']):,.2f}</td>
                                <td class="saldo-baixo">{percentual:.1f}%</td>
                            </tr>
        """
    
    html += """
                        </tbody>
                    </table>
                </div>
                
                <p><strong>Ação recomendada:</strong> Verifique as contas e providencie transferências se necessário.</p>
            </div>
            
            <div class="footer">
                <p>Esta é uma mensagem automática do MeetCall System.</p>
                <p>Não responda este email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html


if __name__ == '__main__':
    main()
