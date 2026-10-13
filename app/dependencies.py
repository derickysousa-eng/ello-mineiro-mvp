"""
Dependências de injeção para o FastAPI.
Extrai e valida o token JWT contido no cookie HttpOnly 'access_token'.
"""

from typing import Any, Dict
from fastapi import Cookie, Depends, HTTPException, status
import pymysql
from app.db import get_db
from app.repositories import usuarios as repo_usuarios
from app.security import decodificar_token_jwt


def get_current_user(
    access_token: str = Cookie(default=None),
    conn: pymysql.Connection = Depends(get_db)
) -> Dict[str, Any]:
    """
    Injeta o usuário autenticado na rota a partir do cookie HttpOnly 'access_token'.
    Lança 401 Unauthorized se o cookie não existir, for inválido, expirado ou usuário inativo.
    """
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticação necessária. Sessão não encontrada ou expirada."
        )

    payload = decodificar_token_jwt(access_token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado."
        )

    try:
        usuario_id = int(payload["sub"])
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identificador de usuário inválido no token."
        )

    usuario = repo_usuarios.buscar_por_id(conn, usuario_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado."
        )

    if not usuario.get("ativo"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Esta conta de usuário está desativada."
        )

    return usuario
