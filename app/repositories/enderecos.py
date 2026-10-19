"""
Repositório de Endereços compatível com a camada de POO.
Delega chamadas para a classe EnderecoRepository e a entidade Endereco.
"""

from typing import Any, Dict, List
import pymysql
from app.domain.entities.endereco import Endereco
from app.repositories.endereco_repository import EnderecoRepository
from app.schemas import EnderecoCreateSchema


def criar_endereco(
    conn: pymysql.Connection,
    usuario_id: int,
    dados: EnderecoCreateSchema
) -> int:
    """
    Insere um endereço vinculado ao usuário com situacao padrão 'ATIVO'.
    Utiliza a entidade Endereco e EnderecoRepository.
    """
    entidade = Endereco(
        usuario_id=usuario_id,
        tipo=dados.tipo or "Residencial",
        cep=dados.cep,
        rua=dados.rua,
        numero=dados.numero,
        bairro=dados.bairro,
        complemento=dados.complemento,
        cidade=dados.cidade,
        uf=dados.uf,
        situacao="ATIVO"
    )
    repo = EnderecoRepository(conn)
    return repo.salvar(entidade)


def listar_por_usuario(
    conn: pymysql.Connection,
    usuario_id: int
) -> List[Dict[str, Any]]:
    """
    Retorna todos os endereços ativos vinculados ao usuário informado em formato de dicionário.
    """
    repo = EnderecoRepository(conn)
    enderecos = repo.listar_por_usuario(usuario_id)
    return [e.to_dict() for e in enderecos]

