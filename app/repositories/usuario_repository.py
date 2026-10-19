"""
Repositório Orientado a Objetos: UsuarioRepository.
Executa operações de persistência da entidade Usuario usando SQL puro parametrizado.
"""

from typing import Optional
import pymysql
from app.domain.entities.usuario import Usuario


class UsuarioRepository:
    """
    Gerencia o acesso a dados e persistência de instâncias de Usuario no banco MySQL.
    Garante queries 100% parametrizadas contra SQL Injection.
    """

    def __init__(self, conn: pymysql.Connection) -> None:
        self.conn = conn

    def salvar(self, usuario: Usuario) -> int:
        """
        Insere uma nova entidade Usuario no banco e atualiza seu ID gerado.
        """
        sql = """
            INSERT INTO Usuarios (
                user_login, email, senha_hash, permissao_nome, nome,
                genero, cpf, rg, data_nasc, telefone, telefone_sec, ativo
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s
            )
        """
        valores = (
            usuario.user_login,
            usuario.email,
            usuario.senha_hash,
            usuario.permissao_nome or "Usuario",
            usuario.nome,
            usuario.genero,
            usuario.cpf,
            usuario.rg,
            usuario.data_nasc,
            usuario.telefone,
            usuario.telefone_sec,
            usuario.ativo
        )
        with self.conn.cursor() as cur:
            cur.execute(sql, valores)
            novo_id = cur.lastrowid
            usuario.id = novo_id
            return novo_id

    def buscar_para_autenticacao(self, identificador: str) -> Optional[Usuario]:
        """
        Busca usuário por user_login ou email para validação de credenciais de login.
        Única consulta autorizada a recuperar a coluna 'senha_hash'.
        """
        sql = """
            SELECT id, user_login, email, senha_hash, permissao_nome,
                   nome, genero, cpf, rg, data_nasc, telefone, telefone_sec, ativo
            FROM Usuarios
            WHERE user_login = %s OR email = %s
            LIMIT 1
        """
        with self.conn.cursor() as cur:
            cur.execute(sql, (identificador, identificador))
            row = cur.fetchone()
            if not row:
                return None
            return self._mapear_linha_para_entidade(row)

    def buscar_por_id(self, usuario_id: int) -> Optional[Usuario]:
        """
        Busca dados cadastrais do usuário para /me e telas do sistema.
        """
        sql = """
            SELECT id, user_login, email, senha_hash, permissao_nome,
                   nome, genero, cpf, rg, data_nasc, telefone, telefone_sec, ativo
            FROM Usuarios
            WHERE id = %s
            LIMIT 1
        """
        with self.conn.cursor() as cur:
            cur.execute(sql, (usuario_id,))
            row = cur.fetchone()
            if not row:
                return None
            return self._mapear_linha_para_entidade(row)

    def verificar_conflito_unicidade(
        self,
        user_login: str,
        email: str,
        cpf: Optional[str] = None,
        rg: Optional[str] = None
    ) -> Optional[str]:
        """
        Verifica se já existe algum registro com o mesmo user_login, email, cpf ou rg.
        Retorna o nome do campo conflitante, ou None se tudo estiver livre.
        """
        with self.conn.cursor() as cur:
            # 1. Checa user_login
            cur.execute("SELECT id FROM Usuarios WHERE user_login = %s LIMIT 1", (user_login,))
            if cur.fetchone():
                return "user_login"

            # 2. Checa email
            cur.execute("SELECT id FROM Usuarios WHERE email = %s LIMIT 1", (email,))
            if cur.fetchone():
                return "email"

            # 3. Checa CPF
            if cpf:
                cur.execute("SELECT id FROM Usuarios WHERE cpf = %s LIMIT 1", (cpf,))
                if cur.fetchone():
                    return "cpf"

            # 4. Checa RG
            if rg:
                cur.execute("SELECT id FROM Usuarios WHERE rg = %s LIMIT 1", (rg,))
                if cur.fetchone():
                    return "rg"

        return None

    @staticmethod
    def _mapear_linha_para_entidade(row: dict) -> Usuario:
        """Método auxiliar interno que hidrata um dicionário SQL em objeto Usuario."""
        return Usuario(
            id=row["id"],
            user_login=row["user_login"],
            email=row["email"],
            senha_hash=row.get("senha_hash", ""),
            permissao_nome=row.get("permissao_nome", "Usuario"),
            nome=row.get("nome", ""),
            genero=row.get("genero"),
            cpf=row.get("cpf", ""),
            rg=row.get("rg", ""),
            data_nasc=row.get("data_nasc"),
            telefone=row.get("telefone"),
            telefone_sec=row.get("telefone_sec"),
            ativo=row.get("ativo", True)
        )
