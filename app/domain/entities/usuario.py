"""
Entidade de Domínio: Usuario.
Aplica Abstração, Composição (com Endereco) e Encapsulamento (proteção de _senha_hash).
"""

from datetime import date
import re
from typing import Any, Dict, Optional, Union
from app.domain.entities.endereco import Endereco
from app.security import verificar_senha


class Usuario:
    """
    Entidade central do sistema de gestão escolar Ello Mineiro.
    Gerencia credenciais, dados pessoais e regras de negócio do usuário.
    """

    def __init__(
        self,
        user_login: str,
        email: str,
        nome: str,
        cpf: str,
        rg: str,
        senha_hash: str,
        genero: Optional[str] = None,
        data_nasc: Optional[Union[date, str]] = None,
        telefone: Optional[str] = None,
        telefone_sec: Optional[str] = None,
        permissao_nome: str = "Usuario",
        ativo: bool = True,
        id: Optional[int] = None,
        endereco: Optional[Endereco] = None
    ) -> None:
        self.id = id
        self.user_login = str(user_login).strip()
        self.email = str(email).strip().lower()
        self.nome = str(nome).strip()
        self.cpf = re.sub(r"\D", "", str(cpf).strip())
        self.rg = str(rg).strip().upper()
        
        # Encapsulamento estrito: a senha com hash nunca fica pública
        self._senha_hash = str(senha_hash).strip() if senha_hash else ""
        
        self.genero = genero.strip() if genero else None
        
        # Conversão defensiva de data
        if isinstance(data_nasc, str) and data_nasc:
            try:
                self.data_nasc = date.fromisoformat(data_nasc)
            except ValueError:
                self.data_nasc = None
        else:
            self.data_nasc = data_nasc

        self.telefone = re.sub(r"\D", "", telefone) if telefone else None
        self.telefone_sec = re.sub(r"\D", "", telefone_sec) if telefone_sec else None
        self.permissao_nome = permissao_nome or "Usuario"
        self.ativo = bool(ativo)

        # Princípio da Composição: um Usuario possui uma referência para seu Endereco
        self.endereco: Optional[Endereco] = endereco

    @property
    def senha_hash(self) -> str:
        """Acesso somente leitura ao hash criptografado."""
        return self._senha_hash

    def atualizar_senha_hash(self, novo_hash: str) -> None:
        """Atualiza o hash da senha de forma controlada."""
        if not novo_hash or not novo_hash.strip():
            raise ValueError("O novo hash de senha não pode ser vazio.")
        self._senha_hash = novo_hash.strip()

    def verificar_senha(self, senha_pura: str) -> bool:
        """
        Método de negócio encapsulado que valida se a senha em texto puro
        corresponde ao hash Argon2id armazenado.
        """
        if not self._senha_hash or not senha_pura:
            return False
        return verificar_senha(senha_pura, self._senha_hash)

    def vincular_endereco(self, endereco: Endereco) -> None:
        """Aplica o princípio de Composição vinculando uma instância de Endereco."""
        if not isinstance(endereco, Endereco):
            raise TypeError("O objeto vinculado deve ser uma instância de Endereco.")
        self.endereco = endereco
        if self.id is not None:
            endereco.usuario_id = self.id

    def desativar(self) -> None:
        """Aplica exclusão lógica da conta (RN03)."""
        self.ativo = False

    def ativar(self) -> None:
        """Reativa a conta do usuário."""
        self.ativo = True

    def obter_nome_formatado(self) -> str:
        """
        Retorna o nome formatado em Title Case inteligente,
        preservando preposições em minúsculas (da, de, do, dos, das, e).
        """
        preposicoes = {"de", "da", "do", "das", "dos", "e"}
        palavras = self.nome.strip().split()
        formatadas = []
        for i, p in enumerate(palavras):
            p_lower = p.lower()
            if i > 0 and p_lower in preposicoes:
                formatadas.append(p_lower)
            else:
                formatadas.append(p_lower.capitalize())
        return " ".join(formatadas)

    def obter_cpf_mascarado(self) -> str:
        """
        Retorna o CPF mascarado para proteção de privacidade na tela (ex: 123.***.***-01).
        """
        if len(self.cpf) == 11:
            return f"{self.cpf[:3]}.***.***-{self.cpf[-2:]}"
        return self.cpf

    def obter_rg_mascarado(self) -> str:
        """
        Retorna o RG mascarado com asteriscos centrais para privacidade.
        """
        if len(self.rg) >= 5:
            return f"{self.rg[:2]}.***-{self.rg[-1]}"
        return self.rg

    def to_dict(self, incluir_privados: bool = False) -> Dict[str, Any]:
        """
        Exporta os atributos da entidade para dicionário serializável.
        Por padrão de segurança, NUNCA exporta a senha_hash.
        """
        data: Dict[str, Any] = {
            "id": self.id,
            "user_login": self.user_login,
            "email": self.email,
            "permissao_nome": self.permissao_nome,
            "nome": self.nome,
            "genero": self.genero,
            "cpf": self.cpf,
            "rg": self.rg,
            "data_nasc": self.data_nasc.isoformat() if isinstance(self.data_nasc, date) else None,
            "telefone": self.telefone,
            "telefone_sec": self.telefone_sec,
            "ativo": self.ativo
        }

        if self.endereco:
            data["endereco"] = self.endereco.to_dict()

        if incluir_privados:
            data["senha_hash"] = self._senha_hash

        return data

    def __repr__(self) -> str:
        return f"<Usuario id={self.id} login='{self.user_login}' email='{self.email}'>"
