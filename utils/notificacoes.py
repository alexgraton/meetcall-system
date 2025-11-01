"""
Sistema de notificações por email
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from database import DatabaseManager


class Notificacoes:
    """Gerenciador de notificações por email"""
    
    def __init__(self, smtp_host=None, smtp_port=None, smtp_user=None, smtp_password=None):
        """
        Inicializa o sistema de notificações
        
        Args:
            smtp_host: Servidor SMTP
            smtp_port: Porta SMTP (587 para TLS, 465 para SSL)
            smtp_user: Usuário SMTP
            smtp_password: Senha SMTP
        """
        self.smtp_host = smtp_host or 'smtp.gmail.com'
        self.smtp_port = smtp_port or 587
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_email = smtp_user
    
    def enviar_email(self, destinatario, assunto, corpo_html, corpo_texto=None):
        """
        Envia um email
        
        Args:
            destinatario: Email do destinatário
            assunto: Assunto do email
            corpo_html: Corpo do email em HTML
            corpo_texto: Corpo do email em texto plano (opcional)
            
        Returns:
            True se enviado com sucesso, False caso contrário
        """
        if not self.smtp_user or not self.smtp_password:
            print("Configurações SMTP não definidas. Email não enviado.")
            return False
        
        try:
            # Criar mensagem
            msg = MIMEMultipart('alternative')
            msg['Subject'] = assunto
            msg['From'] = self.from_email
            msg['To'] = destinatario
            
            # Adicionar versão texto
            if corpo_texto:
                part1 = MIMEText(corpo_texto, 'plain', 'utf-8')
                msg.attach(part1)
            
            # Adicionar versão HTML
            part2 = MIMEText(corpo_html, 'html', 'utf-8')
            msg.attach(part2)
            
            # Enviar
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Erro ao enviar email: {str(e)}")
            return False
    
    @staticmethod
    def verificar_contas_vencendo(dias=7):
        """
        Verifica contas a pagar e receber vencendo em N dias
        
        Args:
            dias: Número de dias de antecedência
            
        Returns:
            dict com contas a pagar e receber vencendo
        """
        db = DatabaseManager()
        data_hoje = datetime.now().date()
        data_limite = data_hoje + timedelta(days=dias)
        
        resultado = {
            'contas_pagar': [],
            'contas_receber': []
        }
        
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Contas a pagar vencendo
            cursor.execute("""
                SELECT 
                    cp.*,
                    f.razao_social as fornecedor,
                    (cp.valor_total - cp.valor_desconto + cp.valor_juros + cp.valor_multa) as valor_final
                FROM contas_pagar cp
                LEFT JOIN fornecedores f ON cp.fornecedor_id = f.id
                WHERE cp.status IN ('pendente', 'vencida')
                AND cp.data_vencimento BETWEEN %s AND %s
                ORDER BY cp.data_vencimento
            """, (data_hoje, data_limite))
            
            resultado['contas_pagar'] = cursor.fetchall()
            
            # Contas a receber vencendo
            cursor.execute("""
                SELECT 
                    cr.*,
                    c.razao_social as cliente,
                    (cr.valor_total - cr.valor_desconto + cr.valor_juros + cr.valor_multa) as valor_final
                FROM contas_receber cr
                LEFT JOIN clientes c ON cr.cliente_id = c.id
                WHERE cr.status IN ('pendente', 'vencida')
                AND cr.data_vencimento BETWEEN %s AND %s
                ORDER BY cr.data_vencimento
            """, (data_hoje, data_limite))
            
            resultado['contas_receber'] = cursor.fetchall()
            cursor.close()
        
        return resultado
    
    @staticmethod
    def verificar_saldo_baixo(limite_percentual=20):
        """
        Verifica contas bancárias com saldo baixo
        
        Args:
            limite_percentual: Percentual do limite de alerta
            
        Returns:
            Lista de contas com saldo baixo
        """
        db = DatabaseManager()
        
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Buscar contas ativas com saldo baixo
            cursor.execute("""
                SELECT 
                    id, banco, agencia, conta, nome,
                    saldo_inicial, saldo_atual,
                    limite_alerta,
                    CASE 
                        WHEN limite_alerta > 0 THEN (saldo_atual / limite_alerta) * 100
                        ELSE NULL
                    END as percentual_saldo
                FROM contas_bancarias
                WHERE is_active = 1
                AND limite_alerta > 0
                AND saldo_atual < limite_alerta
                ORDER BY percentual_saldo
            """)
            
            contas = cursor.fetchall()
            cursor.close()
            
            return contas
    
    def gerar_email_contas_vencendo(self, contas_dados):
        """Gera HTML do email de contas vencendo"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #7c3aed; color: white; padding: 20px; text-align: center; }}
                .content {{ background: #f9fafb; padding: 20px; }}
                .alert {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 15px 0; }}
                table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                th {{ background: #e5e7eb; padding: 10px; text-align: left; }}
                td {{ padding: 10px; border-bottom: 1px solid #e5e7eb; }}
                .valor {{ font-weight: bold; color: #dc2626; }}
                .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #6b7280; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔔 Alerta de Vencimentos</h1>
                    <p>MeetCall System - Gestão Financeira</p>
                </div>
                
                <div class="content">
                    <p>Olá,</p>
                    <p>Este é um alerta automático sobre contas próximas do vencimento:</p>
        """
        
        # Contas a Pagar
        if contas_dados['contas_pagar']:
            html += """
                    <div class="alert">
                        <h3>💰 Contas a Pagar Vencendo</h3>
                        <table>
                            <thead>
                                <tr>
                                    <th>Vencimento</th>
                                    <th>Fornecedor</th>
                                    <th>Descrição</th>
                                    <th>Valor</th>
                                </tr>
                            </thead>
                            <tbody>
            """
            
            for conta in contas_dados['contas_pagar']:
                html += f"""
                                <tr>
                                    <td>{conta['data_vencimento'].strftime('%d/%m/%Y')}</td>
                                    <td>{conta.get('fornecedor', 'N/A')}</td>
                                    <td>{conta['descricao']}</td>
                                    <td class="valor">R$ {float(conta['valor_final']):,.2f}</td>
                                </tr>
                """
            
            total_pagar = sum(float(c['valor_final']) for c in contas_dados['contas_pagar'])
            html += f"""
                            </tbody>
                            <tfoot>
                                <tr>
                                    <th colspan="3">Total a Pagar</th>
                                    <th class="valor">R$ {total_pagar:,.2f}</th>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
            """
        
        # Contas a Receber
        if contas_dados['contas_receber']:
            html += """
                    <div class="alert" style="background: #dbeafe; border-color: #3b82f6;">
                        <h3>📥 Contas a Receber Vencendo</h3>
                        <table>
                            <thead>
                                <tr>
                                    <th>Vencimento</th>
                                    <th>Cliente</th>
                                    <th>Descrição</th>
                                    <th>Valor</th>
                                </tr>
                            </thead>
                            <tbody>
            """
            
            for conta in contas_dados['contas_receber']:
                html += f"""
                                <tr>
                                    <td>{conta['data_vencimento'].strftime('%d/%m/%Y')}</td>
                                    <td>{conta.get('cliente', 'N/A')}</td>
                                    <td>{conta['descricao']}</td>
                                    <td style="color: #059669; font-weight: bold;">R$ {float(conta['valor_final']):,.2f}</td>
                                </tr>
                """
            
            total_receber = sum(float(c['valor_final']) for c in contas_dados['contas_receber'])
            html += f"""
                            </tbody>
                            <tfoot>
                                <tr>
                                    <th colspan="3">Total a Receber</th>
                                    <th style="color: #059669; font-weight: bold;">R$ {total_receber:,.2f}</th>
                                </tr>
                            </tfoot>
                        </table>
                    </div>
            """
        
        html += """
                    <p>Acesse o sistema para mais detalhes e realizar os pagamentos.</p>
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
    
    def enviar_alerta_vencimentos(self, destinatario, dias=7):
        """
        Envia email com alertas de vencimentos
        
        Args:
            destinatario: Email do destinatário
            dias: Dias de antecedência
        """
        contas = self.verificar_contas_vencendo(dias)
        
        total_contas = len(contas['contas_pagar']) + len(contas['contas_receber'])
        
        if total_contas == 0:
            print("Nenhuma conta vencendo no período.")
            return False
        
        assunto = f"⚠️ Alerta: {total_contas} conta(s) vencendo nos próximos {dias} dias"
        corpo_html = self.gerar_email_contas_vencendo(contas)
        
        return self.enviar_email(destinatario, assunto, corpo_html)
