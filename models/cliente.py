"""
Modelo para gerenciar Clientes, contatos e produtos vinculados
"""
from typing import List, Dict, Optional
from database import DatabaseManager

class ClienteModel:
    """Operações CRUD para clientes, seus contatos e produtos"""

    @staticmethod
    def create(dados: Dict) -> Dict:
        """Cria um cliente com contatos e produtos opcionais"""
        try:
            db = DatabaseManager()
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Gerar código se não houver
                if not dados.get('codigo'):
                    cursor.execute("SELECT MAX(CAST(SUBSTRING(codigo, 3) AS UNSIGNED)) FROM clientes")
                    res = cursor.fetchone()
                    next_num = (res[0] or 0) + 1
                    dados['codigo'] = f"C{next_num:05d}"

                query = """
                    INSERT INTO clientes
                    (codigo, nome, razao_social, cnpj, tipo_pessoa, email, telefone, cep, endereco, numero, complemento, bairro, cidade, estado, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)
                """
                cursor.execute(query, (
                    dados.get('codigo'),
                    dados.get('nome'),
                    dados.get('razao_social'),
                    dados.get('cnpj'),
                    dados.get('tipo_pessoa', 'juridica'),
                    dados.get('email'),
                    dados.get('telefone'),
                    dados.get('cep'),
                    dados.get('logradouro'),  # maps to endereco column
                    dados.get('numero'),
                    dados.get('complemento'),
                    dados.get('bairro'),
                    dados.get('cidade'),
                    dados.get('uf')  # maps to estado column
                ))
                conn.commit()
                cliente_id = cursor.lastrowid

                # Inserir contatos
                contatos = dados.get('contatos') or []
                for c in contatos:
                    cursor.execute(
                        "INSERT INTO cliente_contatos (cliente_id, nome, telefone, email, cargo, observacoes) VALUES (%s,%s,%s,%s,%s,%s)",
                        (cliente_id, c.get('nome'), c.get('telefone'), c.get('email'), c.get('cargo'), c.get('observacoes'))
                    )
                
                # Inserir produtos
                produtos = dados.get('produtos') or []
                for p in produtos:
                    cursor.execute(
                        "INSERT INTO cliente_produtos (cliente_id, nome, descricao, valor) VALUES (%s,%s,%s,%s)",
                        (cliente_id, p.get('nome'), p.get('descricao'), p.get('valor'))
                    )
                
                conn.commit()
                return {'success': True, 'message': 'Cliente cadastrado com sucesso', 'codigo': dados['codigo'], 'id': cliente_id}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    @staticmethod
    def get_all(include_inactive: bool = False) -> List[Dict]:
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT c.*, 
                       (SELECT COUNT(*) FROM cliente_produtos WHERE cliente_id = c.id) as produtos_count
                FROM clientes c
                WHERE c.is_active = 1 OR %s
                ORDER BY c.nome
            """
            cursor.execute(query, (include_inactive,))
            return cursor.fetchall()

    @staticmethod
    def get_by_id(cliente_id: int) -> Optional[Dict]:
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM clientes WHERE id = %s", (cliente_id,))
            cliente = cursor.fetchone()
            if not cliente:
                return None
            
            # Buscar contatos
            cursor.execute("SELECT * FROM cliente_contatos WHERE cliente_id = %s ORDER BY id", (cliente_id,))
            cliente['contatos'] = cursor.fetchall()
            
            # Buscar produtos
            cursor.execute("SELECT * FROM cliente_produtos WHERE cliente_id = %s ORDER BY id", (cliente_id,))
            cliente['produtos'] = cursor.fetchall()
            
            return cliente

    @staticmethod
    def update(cliente_id: int, dados: Dict) -> bool:
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                UPDATE clientes
                SET nome=%s, razao_social=%s, cnpj=%s, tipo_pessoa=%s, email=%s, telefone=%s,
                    cep=%s, endereco=%s, numero=%s, complemento=%s, bairro=%s, cidade=%s, estado=%s, updated_at=NOW()
                WHERE id=%s
            """
            cursor.execute(query, (
                dados.get('nome'), dados.get('razao_social'), dados.get('cnpj'), dados.get('tipo_pessoa', 'juridica'),
                dados.get('email'), dados.get('telefone'), dados.get('cep'), dados.get('logradouro'), dados.get('numero'),
                dados.get('complemento'), dados.get('bairro'), dados.get('cidade'), dados.get('uf'), cliente_id
            ))
            
            # Atualizar contatos: apagar e reinserir
            cursor.execute("DELETE FROM cliente_contatos WHERE cliente_id = %s", (cliente_id,))
            contatos = dados.get('contatos') or []
            for c in contatos:
                cursor.execute(
                    "INSERT INTO cliente_contatos (cliente_id, nome, telefone, email, cargo, observacoes) VALUES (%s,%s,%s,%s,%s,%s)",
                    (cliente_id, c.get('nome'), c.get('telefone'), c.get('email'), c.get('cargo'), c.get('observacoes'))
                )
            
            # Atualizar produtos: apagar e reinserir
            cursor.execute("DELETE FROM cliente_produtos WHERE cliente_id = %s", (cliente_id,))
            produtos = dados.get('produtos') or []
            for p in produtos:
                cursor.execute(
                    "INSERT INTO cliente_produtos (cliente_id, nome, descricao, valor) VALUES (%s,%s,%s,%s)",
                    (cliente_id, p.get('nome'), p.get('descricao'), p.get('valor'))
                )
            
            conn.commit()
            return True

    @staticmethod
    def toggle_status(cliente_id: int) -> bool:
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE clientes SET is_active = NOT is_active, updated_at = NOW() WHERE id = %s", (cliente_id,))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete(cliente_id: int) -> bool:
        # Soft delete
        return ClienteModel.toggle_status(cliente_id)
