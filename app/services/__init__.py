"""
Camada de Serviços de Negócio (Service Layer).
Desacopla regras de negócio, criptografia e transações dos controladores HTTP.
"""

from app.services.auth_service import AuthService

__all__ = ["AuthService"]
