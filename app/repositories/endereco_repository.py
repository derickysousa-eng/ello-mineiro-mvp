"""
Repositório Orientado a Objetos: EnderecoRepository.
Executa operações de persistência da entidade Endereco usando SQL puro parametrizado.
"""

from typing import List, Optional
import pymysql
from app.domain.entities.endereco import Endereco


class EnderecoRepository:
    """
    Gerencia o acesso a dados e persistência de instâncias de Endereco no banco MySQL.
    """

    def __init__(self, conn: pymysql.Connection) -> None:
        self.conn = conn

    def salvar(self, endereco: Endereco) -> int:
        """
        Insere a entidade Endereco no banco e atualiza seu ID gerado.
        """
        sql = """
            INSERT INTO Endereco (
                usuario_id, tipo, cep, rua, numero, bairro,
                complemento, cidade, uf, situacao
            ) VALUES (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s
            )
        """
        valores = (
            endereco.usuario_id,
            endereco.tipo or "Residencial",
            endereco.cep,
            endereco.rua,
            endereco.numero,
            endereco.bairro,
            endereco.complemento,
            endereco.cidade,
            endereco.uf,
            endereco.situacao or "ATIVO"
        )
        with self.conn.cursor() as cur:
            cur.execute(sql, valores)
            novo_id = cur.lastrowid
            endereco.id = novo_id
            return novo_id

    def buscar_por_usuario_id(self, usuario_id: int) -> Optional[Endereco]:
        """
        Busca o primeiro endereço ativo do usuário informado e o reconstrói em objeto Endereco.
        """
        sql = """
            SELECT id, usuario_id, tipo, cep, rua, numero, bairro,
                   complemento, cidade, uf, situacao
            FROM Endereco
            WHERE usuario_id = %s AND situacao = 'ATIVO'
            LIMIT 1
        """
        with self.conn.cursor() as cur:
            cur.execute(sql, (usuario_id,))
            row = cur.fetchone()
            if not row:
                return None
            return self._mapear_linha_para_entidade(row)

    def listar_por_usuario(self, usuario_id: int) -> List[Endereco]:
        """
        Retorna todos os endereços ativos do usuário como lista de objetos Endereco.
        """
        sql = """
            SELECT id, usuario_id, tipo, cep, rua, numero, bairro,
                   complemento, cidade, uf, situacao
            FROM Endereco
            WHERE usuario_id = %s AND situacao = 'ATIVO'
            ORDER BY id ASC
        """
        with self.conn.cursor() as cur:
            cur.execute(sql, (usuario_id,))
            rows = cur.fetchall() or []
            return [self._mapear_linha_para_entidade(row) for row in rows]

    @staticmethod
    def _mapear_linha_para_entidade(row: dict) -> Endereco:
        """Método auxiliar interno que hidrata um dicionário SQL em objeto Endereco."""
        return Endereco(
            id=row["id"],
            usuario_id=row.get("usuario_id"),
            tipo=row.get("tipo", "Residencial"),
            cep=row["cep"],
            rua=row["rua"],
            numero=row["numero"],
            bairro=row["bairro"],
            complemento=row.get("complemento"),
            cidade=row["cidade"],
            uf=row["uf"],
            situacao=row.get("situacao", "ATIVO")
        )
