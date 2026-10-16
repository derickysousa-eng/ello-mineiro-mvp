"""
Módulo de Segurança para Rotas de Mutabilidade:
1. Validação de Chave Privada (X-API-Key) para integrações e scripts externos.
2. Handshake transparente para o front-end oficial na mesma origem (RNF18 / Zero atrito).
3. Rate Limiting em memória por IP (RNF07) contra força bruta e abusos.
"""

from collections import defaultdict
import os
import secrets
import time
from typing import Dict, List, Optional
from urllib.parse import urlparse
from fastapi import HTTPException, Request, status

# Carrega a chave privada e configurações de segurança
API_KEY = os.getenv("API_KEY", "ello_priv_key_local_dev_2026")
RATE_LIMIT_LOGIN_MAX = int(os.getenv("RATE_LIMIT_LOGIN_MAX", "10"))
RATE_LIMIT_REGISTER_MAX = int(os.getenv("RATE_LIMIT_REGISTER_MAX", "5"))
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))


class RateLimiter:
    """
    Controlador de taxa de requisições por IP em memória (Sliding Window).
    Mitiga ataques de força bruta e spam de cadastros (RNF07).
    """

    def __init__(self):
        # Dicionário de timestamps: {(ip, endpoint): [timestamp1, timestamp2, ...]}
        self._historico: Dict[str, List[float]] = defaultdict(list)

    def verificar(
        self,
        ip: str,
        rota: str,
        max_requisicoes: int,
        janela_segundos: int = RATE_LIMIT_WINDOW_SECONDS
    ):
        chave = f"{ip}:{rota}"
        agora = time.time()
        corte = agora - janela_segundos

        # Remove requisições mais antigas que a janela
        self._historico[chave] = [t for t in self._historico[chave] if t > corte]

        if len(self._historico[chave]) >= max_requisicoes:
            tempo_espera = int(janela_segundos - (agora - self._historico[chave][0]))
            if tempo_espera <= 0:
                tempo_espera = 1
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Muitas requisições. Limite temporário atingido para esta operação. Tente novamente em {tempo_espera} segundos.",
                headers={"Retry-After": str(tempo_espera)}
            )

        self._historico[chave].append(agora)

    def reset(self):
        """Utilizado em baterias de testes para limpar históricos."""
        self._historico.clear()


# Instância global do RateLimiter
rate_limiter = RateLimiter()


def extrair_ip_cliente(request: Request) -> str:
    """
    Extrai o IP real do cliente considerando cabeçalhos de proxy reverso (Render/Cloudflare).
    """
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        # Pega o primeiro IP da lista (o cliente original)
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"


def verificar_origem_legitima(request: Request) -> bool:
    """
    Verifica se a requisição originou-se legitimamente do front-end do próprio site (mesma origem - RNF18).
    Analisa cabeçalhos nativos do navegador: Sec-Fetch-Site, Origin e Referer.
    """
    host_servidor = request.base_url.netloc.lower()

    # 1. Sec-Fetch-Site emitido por navegadores modernos
    sec_fetch_site = request.headers.get("sec-fetch-site", "").lower()
    if sec_fetch_site == "same-origin":
        return True

    # 2. Verificação de cabeçalho Origin
    origin = request.headers.get("origin")
    if origin:
        try:
            host_origin = urlparse(origin).netloc.lower()
            # Permite se o host for o mesmo do servidor ou equivalentes locais em dev
            if host_origin == host_servidor:
                return True
            if host_servidor.startswith("localhost") and host_origin.startswith("127.0.0.1"):
                return True
            if host_servidor.startswith("127.0.0.1") and host_origin.startswith("localhost"):
                return True
        except Exception:
            return False

    # 3. Verificação de cabeçalho Referer
    referer = request.headers.get("referer")
    if referer:
        try:
            host_referer = urlparse(referer).netloc.lower()
            if host_referer == host_servidor:
                return True
            if host_servidor.startswith("localhost") and host_referer.startswith("127.0.0.1"):
                return True
            if host_servidor.startswith("127.0.0.1") and host_referer.startswith("localhost"):
                return True
        except Exception:
            return False

    return False


def validar_mutabilidade_segura(request: Request):
    """
    Dependência de segurança para rotas de mutabilidade (/api/auth/register, /api/auth/login, etc.).
    Garante que a chamada seja:
    1. Uma integração/script externo autorizado portando a chave correta via 'X-API-Key'.
    2. OU uma requisição originada legitimamente do front-end oficial da aplicação (mesma origem).
    Caso contrário, bloqueia com HTTP 403 Forbidden.
    """
    x_api_key: Optional[str] = request.headers.get("x-api-key")

    # Cenário A: Chamada com cabeçalho X-API-Key (Scripts externos, Postman, Integrações)
    if x_api_key is not None:
        if secrets.compare_digest(x_api_key.strip(), API_KEY.strip()):
            return True
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso não autorizado: chave de API inválida."
        )

    # Cenário B: Chamada vinda do Front-end oficial do site (Zero atrito para o usuário)
    if verificar_origem_legitima(request):
        return True

    # Cenário C: Requisição externa sem chave de API e sem origem legítima
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Acesso não autorizado: requisição externa não identificada ou chave de API ausente no cabeçalho 'X-API-Key'."
    )


def rate_limit_login(request: Request):
    """Aplica limitação de taxa por IP na rota de login."""
    ip = extrair_ip_cliente(request)
    rate_limiter.verificar(ip, "login", max_requisicoes=RATE_LIMIT_LOGIN_MAX)


def rate_limit_register(request: Request):
    """Aplica limitação de taxa por IP na rota de cadastro."""
    ip = extrair_ip_cliente(request)
    rate_limiter.verificar(ip, "register", max_requisicoes=RATE_LIMIT_REGISTER_MAX)
