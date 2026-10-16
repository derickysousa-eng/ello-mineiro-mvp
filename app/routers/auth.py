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
from app.security import criar_token_jwt, gerar_hash_senha, verificar_senha
from app.security_guards import (
    rate_limit_login,
    rate_limit_register,
    validar_mutabilidade_segura,
)

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
    Cadastra um novo usuário no sistema.
    - O perfil atribuído é sempre 'Usuario' (RN02 e RN05).
    - Valida duplicidade de login, e-mail, CPF e RG.
    - Executa a gravação do usuário e endereço em transação atômica.
    """
    conflito = repo_usuarios.verificar_conflito_unicidade(
        conn,
        user_login=dados.user_login,
        email=dados.email,
        cpf=dados.cpf,
        rg=dados.rg
    )
    if conflito:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Já existe um cadastro registrado com este '{conflito}'."
        )

    senha_hash = gerar_hash_senha(dados.senha)

    try:
        # Início da transação atômica (Usuário + Endereço Obrigatório)
        novo_id = repo_usuarios.criar_usuario(conn, dados, senha_hash)
        repo_enderecos.criar_endereco(conn, novo_id, dados.endereco)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro ao salvar o cadastro. Nenhuma alteração foi realizada."
        )

    return {
        "mensagem": "Cadastro realizado com sucesso!",
        "usuario": {
            "id": novo_id,
            "user_login": dados.user_login,
            "email": dados.email,
            "permissao": "Usuario"
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
    Autentica o usuário por user_login ou email.
    Emite o token JWT armazenado em cookie seguro HttpOnly (RF06).
    """
    usuario = repo_usuarios.buscar_para_autenticacao(conn, dados.identificador)

    # Mensagem genérica para prevenir enumeração de contas (RNF07 / RNF10)
    msg_erro = "Identificador ou senha incorretos."

    if not usuario:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg_erro)

    if not usuario.get("ativo"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Esta conta está desativada. Entre em contato com a administração."
        )

    if not verificar_senha(dados.senha, usuario["senha_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg_erro)

    # Gera token JWT
    token = criar_token_jwt(
        usuario_id=usuario["id"],
        user_login=usuario["user_login"],
        permissao=usuario["permissao_nome"]
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
            "id": usuario["id"],
            "user_login": usuario["user_login"],
            "permissao": usuario["permissao_nome"]
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
