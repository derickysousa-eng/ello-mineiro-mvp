"""
Repositório de Endereços com SQL Puro e queries parametrizadas (%s).
"""

from typing import Any, Dict, List
import pymysql
from app.schemas import EnderecoCreateSchema


def criar_endereco(
    conn: pymysql.Connection,
    usuario_id: int,
    dados: EnderecoCreateSchema
) -> int:
    """
    Insere um endereço vinculado ao usuário com situacao padrão 'ATIVO'.
    """
    sql = """
        INSERT INTO Endereco (
            usuario_id, tipo, cep, rua, numero, bairro,
            complemento, cidade, uf, situacao
        ) VALUES (
            %s, %s, %s, %s, %s, %s,
            %s, %s, %s, 'ATIVO'
        )
    """
    valores = (
        usuario_id,
        dados.tipo or "Residencial",
        dados.cep,
        dados.rua,
        dados.numero,
        dados.bairro,
        dados.complemento,
        dados.cidade,
        dados.uf
    )
    with conn.cursor() as cur:
        cur.execute(sql, valores)
        return cur.lastrowid


def listar_por_usuario(
    conn: pymysql.Connection,
    usuario_id: int
) -> List[Dict[str, Any]]:
    """
    Retorna todos os endereços ativos vinculados ao usuário informado.
    """
    sql = """
        SELECT id, tipo, cep, rua, numero, bairro,
               complemento, cidade, uf, situacao
        FROM Endereco
        WHERE usuario_id = %s AND situacao = 'ATIVO'
        ORDER BY id ASC
    """
    with conn.cursor() as cur:
        cur.execute(sql, (usuario_id,))
        return cur.fetchall() or []
