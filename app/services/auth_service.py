"""
Serviço de Autenticação e Gestão de Usuários: AuthService.
Orquestra regras de negócio, composição de entidades, criptografia e transações atômicas.
"""

from typing import Optional
from fastapi import HTTPException, status
import pymysql
from app.domain.entities.endereco import Endereco
from app.domain.entities.usuario import Usuario
from app.repositories.endereco_repository import EnderecoRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.schemas import UsuarioRegisterSchema
from app.security import gerar_hash_senha


class AuthService:
    """
    Camada de Serviço responsável pela regra de negócio de usuários e autenticação.
    Centraliza validações de domínio e controle de transações (commit/rollback).
    """

    def __init__(self, conn: pymysql.Connection) -> None:
        self.conn = conn
        self.usuario_repo = UsuarioRepository(conn)
        self.endereco_repo = EnderecoRepository(conn)

    def cadastrar_usuario(self, dados: UsuarioRegisterSchema) -> Usuario:
        """
        Executa o fluxo completo de cadastro:
        1. Validação de conflito de unicidade (login, email, CPF, RG).
        2. Criptografia de senha com Argon2id.
        3. Instanciação e composição das entidades de domínio Usuario e Endereco.
        4. Gravação atômica em transação única (ACID).
        5. Retorno da entidade persistida.
        """
        # 1. Verifica conflitos de duplicidade
        conflito = self.usuario_repo.verificar_conflito_unicidade(
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

        # 2. Criptografia da senha
        senha_hash = gerar_hash_senha(dados.senha)

        # 3. Instanciação das entidades de domínio
        endereco_entidade = Endereco(
            tipo=dados.endereco.tipo or "Residencial",
            cep=dados.endereco.cep,
            rua=dados.endereco.rua,
            numero=dados.endereco.numero,
            bairro=dados.endereco.bairro,
            complemento=dados.endereco.complemento,
            cidade=dados.endereco.cidade,
            uf=dados.endereco.uf
        )

        usuario_entidade = Usuario(
            user_login=dados.user_login,
            email=dados.email,
            senha_hash=senha_hash,
            nome=dados.nome,
            genero=dados.genero,
            cpf=dados.cpf,
            rg=dados.rg,
            data_nasc=dados.data_nasc,
            telefone=dados.telefone,
            telefone_sec=dados.telefone_sec,
            permissao_nome="Usuario",
            ativo=True
        )

        # 4. Aplica Composição no Domínio
        usuario_entidade.vincular_endereco(endereco_entidade)

        # 5. Execução em Transação Atômica (ACID - Tudo ou Nada)
        try:
            novo_usuario_id = self.usuario_repo.salvar(usuario_entidade)
            endereco_entidade.usuario_id = novo_usuario_id
            self.endereco_repo.salvar(endereco_entidade)
            self.conn.commit()
            return usuario_entidade
        except Exception as e:
            self.conn.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ocorreu um erro ao salvar o cadastro. Nenhuma alteração foi realizada."
            )

    def autenticar(self, identificador: str, senha_pura: str) -> Usuario:
        """
        Autentica credenciais do usuário:
        1. Recupera a entidade Usuario por login ou email.
        2. Executa a validação pelo método encapsulado usuario.verificar_senha().
        3. Verifica se a conta está ativa.
        """
        msg_erro = "Identificador ou senha incorretos."
        usuario = self.usuario_repo.buscar_para_autenticacao(identificador)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=msg_erro
            )

        if not usuario.ativo:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Esta conta está desativada. Entre em contato com a administração."
            )

        # Validação delegada à própria entidade de domínio (Encapsulamento)
        if not usuario.verificar_senha(senha_pura):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=msg_erro
            )

        return usuario

    def obter_usuario_com_endereco(self, usuario_id: int) -> Usuario:
        """
        Recupera o usuário e recompõe seus dados agregados de endereço.
        """
        usuario = self.usuario_repo.buscar_por_id(usuario_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado."
            )

        endereco = self.endereco_repo.buscar_por_usuario_id(usuario_id)
        if endereco:
            usuario.vincular_endereco(endereco)

        return usuario
