"""
Módulo de Segurança e Criptografia.
- Hashing de senhas seguro utilizando Argon2id (salt automático e resistente a ataques de força bruta/GPU).
- Criação e validação de tokens JWT (HS256).
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET") or "chave_secreta_padrao_para_desenvolvimento_ello_2026"
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM") or "HS256"
JWT_EXPIRES_MINUTES = int(os.getenv("JWT_EXPIRES_MINUTES") or "60")

# Inicializa o hasher Argon2id com parâmetros recomendados
_hasher = PasswordHasher()


def gerar_hash_senha(senha: str) -> str:
    """Gera hash seguro com Argon2id."""
    return _hasher.hash(senha)


def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    """Valida se a senha plana informada confere com o hash armazenado."""
    try:
        return _hasher.verify(senha_hash, senha_plana)
    except (VerifyMismatchError, Exception):
        return False


def criar_token_jwt(usuario_id: int, user_login: str, permissao: str) -> str:
    """
    Emite um token JWT contendo as reivindicações mínimas essenciais.
    Sub = id do usuário.
    """
    agora = datetime.now(timezone.utc)
    expiracao = agora + timedelta(minutes=JWT_EXPIRES_MINUTES)
    payload = {
        "sub": str(usuario_id),
        "login": user_login,
        "permissao": permissao,
        "iat": int(agora.timestamp()),
        "exp": int(expiracao.timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decodificar_token_jwt(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodifica e valida assinatura e expiração do JWT.
    Retorna o payload se válido, ou None se inválido/expirado.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except (jwt.PyJWTError, Exception):
        return None
