"""
Entidade de Domínio: Endereco.
Encapsula dados de logradouro e formatação residencial.
"""

from typing import Any, Dict, Optional


class Endereco:
    """
    Representa o domicílio cadastrado de um usuário.
    Participa do relacionamento de Composição com a entidade Usuario.
    """

    def __init__(
        self,
        cep: str,
        rua: str,
        numero: str,
        bairro: str,
        cidade: str,
        uf: str,
        tipo: str = "Residencial",
        complemento: Optional[str] = None,
        situacao: str = "ATIVO",
        id: Optional[int] = None,
        usuario_id: Optional[int] = None
    ) -> None:
        self.id = id
        self.usuario_id = usuario_id
        self.tipo = tipo or "Residencial"
        self.cep = str(cep).strip().replace("-", "")
        self.rua = rua.strip()
        self.numero = numero.strip()
        self.bairro = bairro.strip()
        self.complemento = complemento.strip() if complemento else None
        self.cidade = cidade.strip()
        self.uf = uf.strip().upper()
        self.situacao = situacao.strip().upper() if situacao else "ATIVO"

    def formatar_cep(self) -> str:
        """Retorna o CEP formatado no padrão brasileiro (00000-000)."""
        limpo = self.cep.replace("-", "")
        if len(limpo) == 8:
            return f"{limpo[:5]}-{limpo[5:]}"
        return self.cep

    def obter_endereco_completo(self) -> str:
        """Retorna uma string amigável com a descrição completa do endereço."""
        comp = f", {self.complemento}" if self.complemento else ""
        return f"{self.rua}, {self.numero}{comp} - {self.bairro}, {self.cidade}/{self.uf} ({self.formatar_cep()})"

    def to_dict(self) -> Dict[str, Any]:
        """Converte a entidade para dicionário serializável em JSON."""
        return {
            "id": self.id,
            "tipo": self.tipo,
            "cep": self.cep,
            "rua": self.rua,
            "numero": self.numero,
            "bairro": self.bairro,
            "complemento": self.complemento,
            "cidade": self.cidade,
            "uf": self.uf,
            "situacao": self.situacao
        }

    def __repr__(self) -> str:
        return f"<Endereco id={self.id} cep={self.cep} cidade={self.cidade}/{self.uf}>"
