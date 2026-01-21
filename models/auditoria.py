"""
Modelo de Auditoria - Sistema de Logs Completo
Registra todas as ações dos usuários no sistema
"""
from database import db
import json
from datetime import datetime

class AuditoriaModel:
    """Gerencia logs de auditoria de todas as ações do sistema"""
    
    @staticmethod
    def registrar_acao(tabela, registro_id, acao, usuario_id=None, 
                      dados_anteriores=None, dados_novos=None, ip_address=None):
        """
        Registra uma ação de auditoria
        
        Args:
            tabela: Nome da tabela afetada
            registro_id: ID do registro afetado
            acao: Tipo de ação ('insert', 'update', 'delete', 'login', 'logout', 'view')
            usuario_id: ID do usuário que executou a ação
            dados_anteriores: Dados antes da modificação (dict)
            dados_novos: Dados após a modificação (dict)
            ip_address: Endereço IP do usuário
        """
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Converter dicionários para JSON
            dados_ant_json = json.dumps(dados_anteriores, default=str) if dados_anteriores else None
            dados_nov_json = json.dumps(dados_novos, default=str) if dados_novos else None
            
            query = """
                INSERT INTO auditoria 
                (usuario_id, acao, tabela, registro_id, dados_anteriores, dados_novos, ip_address)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (
                usuario_id,
                acao,
                tabela,
                registro_id,
                dados_ant_json,
                dados_nov_json,
                ip_address
            ))
            
            conn.commit()
            return cursor.lastrowid
    
    @staticmethod
    def registrar_login(usuario_id, email, ip_address, sucesso=True):
        """Registra tentativa de login (sucesso ou falha)"""
        dados = {
            'email': email,
            'sucesso': sucesso,
            'data_hora': datetime.now().isoformat()
        }
        
        return AuditoriaModel.registrar_acao(
            tabela='users',
            registro_id=usuario_id if usuario_id else 0,
            acao='login',
            usuario_id=usuario_id,
            dados_novos=dados,
            ip_address=ip_address
        )
    
    @staticmethod
    def registrar_logout(usuario_id, email, ip_address):
        """Registra logout do usuário"""
        dados = {
            'email': email,
            'data_hora': datetime.now().isoformat()
        }
        
        return AuditoriaModel.registrar_acao(
            tabela='users',
            registro_id=usuario_id,
            acao='logout',
            usuario_id=usuario_id,
            dados_novos=dados,
            ip_address=ip_address
        )
    
    @staticmethod
    def registrar_visualizacao(tabela, registro_id, usuario_id, ip_address):
        """Registra visualização de um registro"""
        return AuditoriaModel.registrar_acao(
            tabela=tabela,
            registro_id=registro_id,
            acao='view',
            usuario_id=usuario_id,
            ip_address=ip_address
        )
    
    @staticmethod
    def listar_logs(filtros=None, limit=100, offset=0):
        """
        Lista logs de auditoria com filtros
        
        Args:
            filtros: dict com filtros (usuario_id, tabela, acao, data_inicio, data_fim)
            limit: Número máximo de registros
            offset: Offset para paginação
        """
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    a.*,
                    u.name as usuario_nome,
                    u.email as usuario_email
                FROM auditoria a
                LEFT JOIN users u ON a.usuario_id = u.id
                WHERE 1=1
            """
            params = []
            
            if filtros:
                if filtros.get('usuario_id'):
                    query += " AND a.usuario_id = %s"
                    params.append(filtros['usuario_id'])
                
                if filtros.get('tabela'):
                    query += " AND a.tabela = %s"
                    params.append(filtros['tabela'])
                
                if filtros.get('acao'):
                    query += " AND a.acao = %s"
                    params.append(filtros['acao'])
                
                if filtros.get('data_inicio'):
                    query += " AND DATE(a.created_at) >= %s"
                    params.append(filtros['data_inicio'])
                
                if filtros.get('data_fim'):
                    query += " AND DATE(a.created_at) <= %s"
                    params.append(filtros['data_fim'])
                
                if filtros.get('registro_id'):
                    query += " AND a.registro_id = %s"
                    params.append(filtros['registro_id'])
            
            query += " ORDER BY a.created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            logs = cursor.fetchall()
            
            # Processar JSON
            for log in logs:
                if log['dados_anteriores']:
                    try:
                        log['dados_anteriores'] = json.loads(log['dados_anteriores'])
                    except:
                        pass
                
                if log['dados_novos']:
                    try:
                        log['dados_novos'] = json.loads(log['dados_novos'])
                    except:
                        pass
            
            return logs
    
    @staticmethod
    def contar_logs(filtros=None):
        """Conta total de logs com filtros"""
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT COUNT(*) FROM auditoria WHERE 1=1"
            params = []
            
            if filtros:
                if filtros.get('usuario_id'):
                    query += " AND usuario_id = %s"
                    params.append(filtros['usuario_id'])
                
                if filtros.get('tabela'):
                    query += " AND tabela = %s"
                    params.append(filtros['tabela'])
                
                if filtros.get('acao'):
                    query += " AND acao = %s"
                    params.append(filtros['acao'])
                
                if filtros.get('data_inicio'):
                    query += " AND DATE(data_hora) >= %s"
                    params.append(filtros['data_inicio'])
                
                if filtros.get('data_fim'):
                    query += " AND DATE(data_hora) <= %s"
                    params.append(filtros['data_fim'])
            
            cursor.execute(query, params)
            return cursor.fetchone()[0]
    
    @staticmethod
    def obter_historico_registro(tabela, registro_id):
        """Obtém todo o histórico de um registro específico"""
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    a.*,
                    u.name as usuario_nome,
                    u.email as usuario_email
                FROM auditoria a
                LEFT JOIN users u ON a.usuario_id = u.id
                WHERE a.tabela = %s AND a.registro_id = %s
                ORDER BY a.created_at ASC
            """
            
            cursor.execute(query, (tabela, registro_id))
            historico = cursor.fetchall()
            
            # Processar JSON
            for log in historico:
                if log['dados_anteriores']:
                    try:
                        log['dados_anteriores'] = json.loads(log['dados_anteriores'])
                    except:
                        pass
                
                if log['dados_novos']:
                    try:
                        log['dados_novos'] = json.loads(log['dados_novos'])
                    except:
                        pass
            
            return historico
    
    @staticmethod
    def obter_atividade_usuario(usuario_id, limit=50):
        """Obtém as últimas atividades de um usuário"""
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    a.*,
                    u.name as usuario_nome,
                    u.email as usuario_email
                FROM auditoria a
                LEFT JOIN users u ON a.usuario_id = u.id
                WHERE a.usuario_id = %s
                ORDER BY a.created_at DESC
                LIMIT %s
            """
            
            cursor.execute(query, (usuario_id, limit))
            return cursor.fetchall()
    
    @staticmethod
    def obter_estatisticas():
        """Retorna estatísticas gerais de auditoria"""
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            
            # Total de ações por tipo
            cursor.execute("""
                SELECT acao, COUNT(*) as total
                FROM auditoria
                GROUP BY acao
            """)
            acoes = cursor.fetchall()
            
            # Usuários mais ativos
            cursor.execute("""
                SELECT 
                    u.name,
                    u.email,
                    COUNT(*) as total_acoes
                FROM auditoria a
                INNER JOIN users u ON a.usuario_id = u.id
                GROUP BY u.id, u.name, u.email
                ORDER BY total_acoes DESC
                LIMIT 10
            """)
            usuarios_ativos = cursor.fetchall()
            
            # Tabelas mais modificadas
            cursor.execute("""
                SELECT tabela, COUNT(*) as total
                FROM auditoria
                WHERE acao IN ('insert', 'update', 'delete')
                GROUP BY tabela
                ORDER BY total DESC
                LIMIT 10
            """)
            tabelas = cursor.fetchall()
            
            return {
                'acoes': acoes,
                'usuarios_ativos': usuarios_ativos,
                'tabelas_modificadas': tabelas
            }
