"""
Repositório de Usuários com SQL Puro e queries 100% parametrizadas (%s).
Regras estritas (doc 02, seção 7):
- Sem interpolação de strings em queries (prevenção contra SQL Injection).
- Sem 'SELECT *'; colunas sempre explícitas.
- senha_hash só é lida no fluxo de login.
"""

from typing import Any, Dict, Optional, Tuple
import pymysql
from app.schemas import UsuarioRegisterSchema


def buscar_para_autenticacao(conn: pymysql.Connection, identificador: str) -> Optional[Dict[str, Any]]:
    """
    Busca usuário por user_login ou email para validação de credenciais de login.
    Única consulta autorizada a recuperar a coluna 'senha_hash'.
    """
    sql = """
        SELECT id, user_login, email, senha_hash, permissao_nome, ativo
        FROM Usuarios
        WHERE user_login = %s OR email = %s
        LIMIT 1
    """
    with conn.cursor() as cur:
        cur.execute(sql, (identificador, identificador))
        return cur.fetchone()


def buscar_por_id(conn: pymysql.Connection, usuario_id: int) -> Optional[Dict[str, Any]]:
    """
    Busca dados cadastrais do usuário para /me e telas do sistema.
    NUNCA inclui senha_hash.
    """
    sql = """
        SELECT id, user_login, email, permissao_nome, nome, genero,
               cpf, rg, data_nasc, telefone, telefone_sec, ativo
        FROM Usuarios
        WHERE id = %s
        LIMIT 1
    """
    with conn.cursor() as cur:
        cur.execute(sql, (usuario_id,))
        return cur.fetchone()


def verificar_conflito_unicidade(
    conn: pymysql.Connection,
    user_login: str,
    email: str,
    cpf: Optional[str] = None,
    rg: Optional[str] = None
) -> Optional[str]:
    """
    Verifica se já existe algum registro com o mesmo user_login, email, cpf ou rg.
    Retorna o nome do campo conflitante, ou None se tudo estiver livre.
    """
    with conn.cursor() as cur:
        # 1. Checa user_login
        cur.execute("SELECT id FROM Usuarios WHERE user_login = %s LIMIT 1", (user_login,))
        if cur.fetchone():
            return "user_login"

        # 2. Checa email
        cur.execute("SELECT id FROM Usuarios WHERE email = %s LIMIT 1", (email,))
        if cur.fetchone():
            return "email"

        # 3. Checa CPF (se informado)
        if cpf:
            cur.execute("SELECT id FROM Usuarios WHERE cpf = %s LIMIT 1", (cpf,))
            if cur.fetchone():
                return "cpf"

        # 4. Checa RG (se informado)
        if rg:
            cur.execute("SELECT id FROM Usuarios WHERE rg = %s LIMIT 1", (rg,))
            if cur.fetchone():
                return "rg"

    return None


def criar_usuario(
    conn: pymysql.Connection,
    dados: UsuarioRegisterSchema,
    senha_hash: str
) -> int:
    """
    Insere o novo usuário no banco com o perfil padrão fixo 'Usuario' (RN02 e RN05).
    Retorna o ID gerado pelo banco de dados (lastrowid).
    """
    sql = """
        INSERT INTO Usuarios (
            user_login, email, senha_hash, permissao_nome, nome,
            genero, cpf, rg, data_nasc, telefone, telefone_sec, ativo
        ) VALUES (
            %s, %s, %s, 'Usuario', %s,
            %s, %s, %s, %s, %s, %s, TRUE
        )
    """
    valores = (
        dados.user_login,
        dados.email,
        senha_hash,
        dados.nome,
        dados.genero,
        dados.cpf,
        dados.rg,
        dados.data_nasc,
        dados.telefone,
        dados.telefone_sec
    )
    with conn.cursor() as cur:
        cur.execute(sql, valores)
        return cur.lastrowid
