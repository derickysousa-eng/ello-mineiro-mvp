"""
Ponto de entrada principal da aplicação FastAPI.
- Configura rotas da API (/api/auth, /api/me).
- Disponibiliza rota de monitoramento /health.
- Serve páginas HTML e arquivos estáticos (mesma origem, deploy único sem CORS).
"""

import os
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from app.db import get_raw_connection
from app.routers.auth import router as auth_router
from app.routers.me import router as me_router

app = FastAPI(
    title="Escola Particular Ello Mineiro — API",
    description="API REST para controle de autenticação e gestão de usuários (MVP).",
    version="1.0.0"
)

# Registra os roteadores da API sob o prefixo /api
app.include_router(auth_router, prefix="/api")
app.include_router(me_router, prefix="/api")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Traduz erros técnicos de validação do Pydantic para mensagens claras e amigáveis em português.
    """
    mapa_campos = {
        "user_login": "Nome de Usuário",
        "email": "E-mail",
        "senha": "Senha",
        "nome": "Nome Completo",
        "genero": "Gênero",
        "cpf": "CPF",
        "rg": "RG",
        "data_nasc": "Data de Nascimento",
        "telefone": "Telefone Celular",
        "telefone_sec": "Telefone Secundário",
        "endereco": "Endereço",
        "cep": "CEP",
        "rua": "Logradouro/Rua",
        "numero": "Número",
        "bairro": "Bairro",
        "complemento": "Complemento",
        "cidade": "Cidade",
        "uf": "Estado (UF)"
    }

    erros_amigaveis = []
    for erro in exc.errors():
        loc = erro.get("loc", [])
        campo_raw = str(loc[-1]) if loc else "campo"
        campo_nome = mapa_campos.get(campo_raw, campo_raw)
        tipo = erro.get("type", "")
        msg_original = erro.get("msg", "")

        if "value is not a valid email address" in msg_original or tipo.startswith("value_error.email") or campo_raw == "email":
            erros_amigaveis.append("O e-mail informado é inválido. Certifique-se de incluir um formato correto (exemplo: usuario@dominio.com).")
        elif "missing" in tipo or "Field required" in msg_original:
            erros_amigaveis.append(f"O campo '{campo_nome}' é obrigatório.")
        elif "string_too_short" in tipo:
            min_len = erro.get("ctx", {}).get("min_length", "")
            erros_amigaveis.append(f"O campo '{campo_nome}' deve ter no mínimo {min_len} caracteres.")
        elif "string_too_long" in tipo:
            max_len = erro.get("ctx", {}).get("max_length", "")
            erros_amigaveis.append(f"O campo '{campo_nome}' deve ter no máximo {max_len} caracteres.")
        elif msg_original.startswith("Value error, "):
            erros_amigaveis.append(msg_original.replace("Value error, ", "").strip())
        else:
            erros_amigaveis.append(f"Valor inválido para o campo '{campo_nome}'.")

    # Retorna mensagem amigável consolidada
    mensagem_final = " | ".join(dict.fromkeys(erros_amigaveis)) if erros_amigaveis else "Dados informados são inválidos. Por favor, revise os campos."
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": mensagem_final}
    )


# Monta diretório de arquivos estáticos (CSS, JS, imagens)
frontend_static_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "static")
if os.path.exists(frontend_static_dir):
    app.mount("/static", StaticFiles(directory=frontend_static_dir), name="static")


@app.get("/health", tags=["Monitoramento"], summary="Verificação de integridade da API e do Banco")
def health_check():
    """
    Testa se a API está respondendo e executa uma consulta simples no banco de dados.
    """
    try:
        conn = get_raw_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1 AS status")
            resultado = cur.fetchone()
        conn.close()
        return {
            "status": "online",
            "banco": "conectado",
            "db_check": resultado.get("status") == 1
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Falha na conexão com o banco de dados: {str(e)}"
        )


# =====================================================================
# Rotas para entrega das páginas HTML (Frontend Estático na Mesma Origem)
# =====================================================================

frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")


@app.get("/", include_in_schema=False)
def pagina_login():
    """Retorna a tela de Login."""
    caminho = os.path.join(frontend_dir, "index.html")
    if os.path.exists(caminho):
        return FileResponse(caminho)
    return {"mensagem": "Página de login em construção."}


@app.get("/cadastro", include_in_schema=False)
def pagina_cadastro():
    """Retorna a tela de Cadastro."""
    caminho = os.path.join(frontend_dir, "cadastro.html")
    if os.path.exists(caminho):
        return FileResponse(caminho)
    return {"mensagem": "Página de cadastro em construção."}


@app.get("/home", include_in_schema=False)
def pagina_home():
    """Retorna a tela de Home / Dashboard."""
    caminho = os.path.join(frontend_dir, "home.html")
    if os.path.exists(caminho):
        return FileResponse(caminho)
    return {"mensagem": "Página inicial em construção."}


@app.get("/recuperacao", include_in_schema=False)
def pagina_recuperacao():
    """Retorna a tela de Recuperação de Senha."""
    caminho = os.path.join(frontend_dir, "recuperacao.html")
    if os.path.exists(caminho):
        return FileResponse(caminho)
    return {"mensagem": "Página de recuperação em construção."}

