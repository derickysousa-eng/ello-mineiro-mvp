"""
Rota protegida /api/me:
Retorna os dados cadastrais do usuário autenticado a partir do cookie HttpOnly.
"""

from typing import Any, Dict
from fastapi import APIRouter, Depends
import pymysql
from app.db import get_db
from app.dependencies import get_current_user
from app.repositories import enderecos as repo_enderecos
from app.schemas import UsuarioResponseSchema
from app.services.auth_service import AuthService

router = APIRouter(prefix="", tags=["Usuário"])


@router.get(
    "/me",
    response_model=UsuarioResponseSchema,
    summary="Obter dados do usuário autenticado"
)
def obter_usuario_logado(
    usuario: Dict[str, Any] = Depends(get_current_user),
    conn: pymysql.Connection = Depends(get_db)
):
    """
    Retorna os dados cadastrais e endereços do usuário associado à sessão atual.
    A senha nunca é retornada.
    """
    auth_service = AuthService(conn)
    usuario_entidade = auth_service.obter_usuario_com_endereco(usuario["id"])
    dados = usuario_entidade.to_dict()
    enderecos = repo_enderecos.listar_por_usuario(conn, usuario["id"])
    dados["enderecos"] = enderecos
    return dados

