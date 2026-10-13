"""
Ponto de entrada principal da aplicação FastAPI.
- Configura rotas da API (/api/auth, /api/me).
- Disponibiliza rota de monitoramento /health.
- Serve páginas HTML e arquivos estáticos (mesma origem, deploy único sem CORS).
"""

import os
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse
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
