"""
Repositório de Usuários com SQL Puro e queries 100% parametrizadas (%s).
Camada compatível orientada a objetos delegada para UsuarioRepository.
"""

from typing import Any, Dict, Optional
import pymysql
from app.domain.entities.usuario import Usuario
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas import UsuarioRegisterSchema


def buscar_para_autenticacao(conn: pymysql.Connection, identificador: str) -> Optional[Dict[str, Any]]:
    """
    Busca usuário por user_login ou email para validação de credenciais de login.
    """
    repo = UsuarioRepository(conn)
    usuario = repo.buscar_para_autenticacao(identificador)
    return usuario.to_dict(incluir_privados=True) if usuario else None


def buscar_por_id(conn: pymysql.Connection, usuario_id: int) -> Optional[Dict[str, Any]]:
    """
    Busca dados cadastrais do usuário para /me e telas do sistema.
    """
    repo = UsuarioRepository(conn)
    usuario = repo.buscar_por_id(usuario_id)
    return usuario.to_dict() if usuario else None


def verificar_conflito_unicidade(
    conn: pymysql.Connection,
    user_login: str,
    email: str,
    cpf: Optional[str] = None,
    rg: Optional[str] = None
) -> Optional[str]:
    """
    Verifica se já existe algum registro com o mesmo user_login, email, cpf ou rg.
    """
    repo = UsuarioRepository(conn)
    return repo.verificar_conflito_unicidade(user_login, email, cpf, rg)


def criar_usuario(
    conn: pymysql.Connection,
    dados: UsuarioRegisterSchema,
    senha_hash: str
) -> int:
    """
    Insere o novo usuário no banco criando uma instância da entidade Usuario.
    """
    repo = UsuarioRepository(conn)
    usuario = Usuario(
        user_login=dados.user_login,
        email=dados.email,
        nome=dados.nome,
        cpf=dados.cpf,
        rg=dados.rg,
        senha_hash=senha_hash,
        genero=dados.genero,
        data_nasc=dados.data_nasc,
        telefone=dados.telefone,
        telefone_sec=dados.telefone_sec,
        permissao_nome="Usuario"
    )
    return repo.salvar(usuario)
