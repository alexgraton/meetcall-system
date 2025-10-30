"""
Modelo para gerenciar Fornecedores e contatos (multi-contact)
"""
from typing import List, Dict, Optional
from database import DatabaseManager

class FornecedorModel:
    """Operações CRUD para fornecedores e seus contatos"""

    @staticmethod
    def create(dados: Dict) -> int:
        """Cria um fornecedor. `dados` deve conter chaves como nome, razao_social, cnpj, email, telefone, endereco, cidade, estado, cep, tipo_pessoa, codigo opcional."""
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            # gerar codigo se não houver
            if not dados.get('codigo'):
                cursor.execute("SELECT MAX(CAST(SUBSTRING(codigo, 3) AS UNSIGNED)) FROM fornecedores")
                res = cursor.fetchone()
                next_num = (res[0] or 0) + 1
                dados['codigo'] = f"F{next_num:05d}"

            query = """
                INSERT INTO fornecedores
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
                dados.get('endereco'),
                dados.get('numero'),
                dados.get('complemento'),
                dados.get('bairro'),
                dados.get('cidade'),
                dados.get('estado')
            ))
            conn.commit()
            fornecedor_id = cursor.lastrowid

            # inserir contatos se fornecidos
            contatos = dados.get('contatos') or []
            for c in contatos:
                cursor.execute(
                    "INSERT INTO fornecedor_contatos (fornecedor_id, nome, telefone, email, cargo, observacoes) VALUES (%s,%s,%s,%s,%s,%s)",
                    (fornecedor_id, c.get('nome'), c.get('telefone'), c.get('email'), c.get('cargo'), c.get('observacoes'))
                )
            conn.commit()
            return fornecedor_id

    @staticmethod
    def get_all(include_inactive: bool = False) -> List[Dict]:
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            if include_inactive:
                cursor.execute("SELECT * FROM fornecedores ORDER BY nome")
            else:
                cursor.execute("SELECT * FROM fornecedores WHERE is_active = 1 ORDER BY nome")
            return cursor.fetchall()

    @staticmethod
    def get_by_id(fornecedor_id: int) -> Optional[Dict]:
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM fornecedores WHERE id = %s", (fornecedor_id,))
            fornecedor = cursor.fetchone()
            if not fornecedor:
                return None
            cursor.execute("SELECT * FROM fornecedor_contatos WHERE fornecedor_id = %s ORDER BY id", (fornecedor_id,))
            fornecedor['contatos'] = cursor.fetchall()
            return fornecedor

    @staticmethod
    def update(fornecedor_id: int, dados: Dict) -> bool:
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                UPDATE fornecedores
                SET nome=%s, razao_social=%s, cnpj=%s, tipo_pessoa=%s, email=%s, telefone=%s,
                    cep=%s, endereco=%s, numero=%s, complemento=%s, bairro=%s, cidade=%s, estado=%s, updated_at=NOW()
                WHERE id=%s
            """
            cursor.execute(query, (
                dados.get('nome'), dados.get('razao_social'), dados.get('cnpj'), dados.get('tipo_pessoa', 'juridica'),
                dados.get('email'), dados.get('telefone'), dados.get('cep'), dados.get('endereco'), dados.get('numero'),
                dados.get('complemento'), dados.get('bairro'), dados.get('cidade'), dados.get('estado'), fornecedor_id
            ))
            # atualizar contatos: estratégia simples -> apagar os existentes e inserir os novos
            cursor.execute("DELETE FROM fornecedor_contatos WHERE fornecedor_id = %s", (fornecedor_id,))
            contatos = dados.get('contatos') or []
            for c in contatos:
                cursor.execute(
                    "INSERT INTO fornecedor_contatos (fornecedor_id, nome, telefone, email, cargo, observacoes) VALUES (%s,%s,%s,%s,%s,%s)",
                    (fornecedor_id, c.get('nome'), c.get('telefone'), c.get('email'), c.get('cargo'), c.get('observacoes'))
                )
            conn.commit()
            return True

    @staticmethod
    def toggle_status(fornecedor_id: int) -> bool:
        db = DatabaseManager()
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE fornecedores SET is_active = NOT is_active, updated_at = NOW() WHERE id = %s", (fornecedor_id,))
            conn.commit()
            return cursor.rowcount > 0

    @staticmethod
    def delete(fornecedor_id: int) -> bool:
        # soft delete
        return FornecedorModel.toggle_status(fornecedor_id)
