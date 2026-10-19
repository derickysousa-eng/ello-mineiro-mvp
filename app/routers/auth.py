"""
Rotas de Autenticação (/api/auth):
- POST /api/auth/register: Criação de novo usuário com perfil fixo 'Usuario'.
- POST /api/auth/login: Validação de credenciais e emissão de cookie HttpOnly.
- POST /api/auth/logout: Revogação do cookie de sessão.
"""

import os
from fastapi import APIRouter, Body, Depends, HTTPException, Response, status
import pymysql
from app.db import get_db
from app.repositories import enderecos as repo_enderecos
from app.repositories import usuarios as repo_usuarios
from app.schemas import UsuarioLoginSchema, UsuarioRegisterSchema
from app.security import criar_token_jwt
from app.security_guards import (
    rate_limit_login,
    rate_limit_register,
    validar_mutabilidade_segura,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Autenticação"])

COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() in ("true", "1", "yes")
JWT_EXPIRES_MINUTES = int(os.getenv("JWT_EXPIRES_MINUTES", "60"))

# Exemplos explícitos para renderização perfeita no Postman e Swagger
EXEMPLO_CADASTRO = {
    "user_login": "carlos.silva",
    "email": "carlos.silva@exemplo.com",
    "senha": "SenhaForte123!",
    "nome": "Carlos da Silva",
    "genero": "Masculino",
    "cpf": "12345678901",
    "rg": "MG12345678",
    "data_nasc": "2002-05-20",
    "telefone": "31999998888",
    "telefone_sec": "31988887777",
    "endereco": {
        "tipo": "Residencial",
        "cep": "30110000",
        "rua": "Rua Mato Grosso",
        "numero": "142",
        "bairro": "Belvedere",
        "complemento": "Apto 201",
        "cidade": "Belo Horizonte",
        "uf": "MG"
    }
}

EXEMPLO_LOGIN = {
    "identificador": "carlos.silva",
    "senha": "SenhaForte123!"
}


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Cadastro de novos usuários",
    dependencies=[Depends(validar_mutabilidade_segura), Depends(rate_limit_register)]
)
def registrar_usuario(
    dados: UsuarioRegisterSchema = Body(
        ...,
        openapi_examples={
            "cadastro_completo": {
                "summary": "Cadastro Completo com Endereço",
                "description": "Exemplo com todos os dados preenchidos incluindo endereço",
                "value": EXEMPLO_CADASTRO
            }
        }
    ),
    conn: pymysql.Connection = Depends(get_db)
):
    """
    Cadastra um novo usuário no sistema através do serviço de domínio AuthService.
    - O perfil atribuído é sempre 'Usuario' (RN02 e RN05).
    - Valida duplicidade de login, e-mail, CPF e RG.
    - Executa a gravação do usuário e endereço em transação atômica.
    """
    auth_service = AuthService(conn)
    usuario_criado = auth_service.cadastrar_usuario(dados)

    return {
        "mensagem": "Cadastro realizado com sucesso!",
        "usuario": {
            "id": usuario_criado.id,
            "user_login": usuario_criado.user_login,
            "email": usuario_criado.email,
            "permissao": usuario_criado.permissao_nome
        }
    }


@router.post(
    "/login",
    summary="Autenticação de usuário e início de sessão",
    dependencies=[Depends(validar_mutabilidade_segura), Depends(rate_limit_login)]
)
def login(
    dados: UsuarioLoginSchema = Body(
        ...,
        openapi_examples={
            "login_padrao": {
                "summary": "Login Padrão",
                "description": "Exemplo de autenticação usando user_login ou email",
                "value": EXEMPLO_LOGIN
            }
        }
    ),
    response: Response = None,
    conn: pymysql.Connection = Depends(get_db)
):
    """
    Autentica o usuário por user_login ou email via AuthService.
    Emite o token JWT armazenado em cookie seguro HttpOnly (RF06).
    """
    auth_service = AuthService(conn)
    usuario = auth_service.autenticar(dados.identificador, dados.senha)

    # Gera token JWT
    token = criar_token_jwt(
        usuario_id=usuario.id,
        user_login=usuario.user_login,
        permissao=usuario.permissao_nome
    )

    # Grava o token em cookie seguro HttpOnly
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=COOKIE_SECURE,  # False em localhost; True quando em produção HTTPS
        samesite="lax",
        max_age=JWT_EXPIRES_MINUTES * 60,
        path="/"
    )

    return {
        "mensagem": "Login realizado com sucesso!",
        "usuario": {
            "id": usuario.id,
            "user_login": usuario.user_login,
            "permissao": usuario.permissao_nome
        }
    }


@router.post(
    "/logout",
    summary="Encerramento de sessão",
    dependencies=[Depends(validar_mutabilidade_segura)]
)
def logout(response: Response):
    """
    Remove o cookie de sessão HttpOnly.
    """
    response.delete_cookie(
        key="access_token",
        path="/"
    )
    return {"mensagem": "Sessão encerrada com sucesso!"}
