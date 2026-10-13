"""
Esquemas de dados e contratos de validação da API usando Pydantic.
Garante que requisições inválidas sejam rejeitadas antes de tocar no banco.
"""

from datetime import date
import re
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class EnderecoCreateSchema(BaseModel):
    tipo: str = Field(default="Residencial", max_length=20)
    cep: str = Field(min_length=8, max_length=8, description="8 dígitos numéricos")
    rua: str = Field(min_length=1, max_length=100)
    numero: str = Field(min_length=1, max_length=20)
    bairro: str = Field(min_length=1, max_length=100)
    complemento: Optional[str] = Field(default=None, max_length=255)
    cidade: str = Field(min_length=1, max_length=50)
    uf: str = Field(min_length=2, max_length=2, description="Sigla do estado (2 letras)")

    @field_validator("cep")
    @classmethod
    def validar_cep(cls, v: str) -> str:
        limpo = re.sub(r"\D", "", v)
        if len(limpo) != 8:
            raise ValueError("O CEP deve conter exatamente 8 dígitos numéricos.")
        return limpo

    @field_validator("uf")
    @classmethod
    def validar_uf(cls, v: str) -> str:
        return v.strip().upper()


class EnderecoResponseSchema(BaseModel):
    id: int
    tipo: str = "Residencial"
    cep: str
    rua: str
    numero: str
    bairro: str
    complemento: Optional[str] = None
    cidade: str
    uf: str
    situacao: str = "ATIVO"


class UsuarioRegisterSchema(BaseModel):
    user_login: str = Field(min_length=3, max_length=30)
    email: EmailStr
    senha: str = Field(min_length=8, max_length=128)
    nome: str = Field(min_length=2, max_length=100)
    genero: Optional[str] = Field(default=None, max_length=20)
    cpf: Optional[str] = Field(default=None, max_length=14)
    rg: Optional[str] = Field(default=None, max_length=30)
    data_nasc: Optional[date] = None
    telefone: Optional[str] = Field(default=None, max_length=15)
    telefone_sec: Optional[str] = Field(default=None, max_length=15)
    endereco: EnderecoCreateSchema  # OBRIGATÓRIO: todo usuário cadastrado deve ter ao menos um endereço vinculado

    @field_validator("user_login")
    @classmethod
    def validar_user_login(cls, v: str) -> str:
        login_limpo = v.strip().lower()
        if not re.match(r"^[a-z0-9._]{3,30}$", login_limpo):
            raise ValueError(
                "O nome de usuário deve conter entre 3 e 30 caracteres e usar apenas letras minúsculas, números, ponto ou sublinhado."
            )
        return login_limpo

    @field_validator("cpf")
    @classmethod
    def validar_cpf(cls, v: Optional[str]) -> Optional[str]:
        if v:
            limpo = re.sub(r"\D", "", v)
            if len(limpo) != 11:
                raise ValueError("O CPF deve conter exatamente 11 dígitos numéricos.")
            return limpo
        return None

    @field_validator("telefone", "telefone_sec")
    @classmethod
    def validar_telefone(cls, v: Optional[str]) -> Optional[str]:
        if v:
            limpo = re.sub(r"\D", "", v)
            if len(limpo) != 11:
                raise ValueError("O telefone deve conter exatamente 11 dígitos numéricos (DDD + número).")
            return limpo
        return None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
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
            ]
        }
    }


class UsuarioLoginSchema(BaseModel):
    identificador: str = Field(min_length=3, max_length=100, description="Nome de usuário ou E-mail")
    senha: str = Field(min_length=1, max_length=128)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "identificador": "carlos.silva",
                    "senha": "SenhaForte123!"
                }
            ]
        }
    }


class UsuarioResponseSchema(BaseModel):
    id: int
    user_login: str
    email: str
    nome: str
    permissao_nome: str
    genero: Optional[str] = None
    cpf: Optional[str] = None
    rg: Optional[str] = None
    data_nasc: Optional[date] = None
    telefone: Optional[str] = None
    telefone_sec: Optional[str] = None
    ativo: bool
    enderecos: List[EnderecoResponseSchema] = []
