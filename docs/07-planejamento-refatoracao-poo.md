# Arquitetura Orientada a Objetos (POO) — Implementação e Guia de Manutenção

> **Documento:** `docs/07-planejamento-refatoracao-poo.md`  
> **Status:** Concluído, Integrado e Homologado com 100% de Sucesso (11/11 testes automatizados)  
> **Branch de Referência:** `feature/refatoracao-poo`  
> **Objetivo:** Documentar detalhadamente a lógica empregada, as classes de domínio, os padrões de projeto adotados (Repository e Service Layer) e o guia passo a passo para futuras análises, correções e extensões.

---

## 1. Visão Geral da Arquitetura Orientada a Objetos

A refatoração elevou o backend da aplicação de uma estrutura puramente funcional/modular para uma **Arquitetura em Camadas Orientada a Objetos**, mantendo o banco de dados relacional com SQL puro parametrizado (`PyMySQL`) e zero quebra de contratos para a interface web.

```
┌────────────────────────────────────────────────────────────────────────┐
│                   CONTROLADORES WEB (FastAPI Routers)                  │
│               app/routers/auth.py  |  app/routers/me.py                │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                         Injeta e invoca métodos
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                 CAMADA DE SERVIÇOS (Service Layer - POO)               │
│                  class AuthService (app/services/)                     │
│  - Orquestra regras de negócio e validações cruzadas                   │
│  - Gerencia transações atômicas ACID (commit e rollback)               │
│  - Aplica composição de objetos de domínio                             │
└───────────────────┬────────────────────────────────┬───────────────────┘
                    │                                │
             Persiste/Recupera                Instancia/Opera
                    │                                │
                    ▼                                ▼
┌──────────────────────────────────┐ ┌──────────────────────────────────┐
│   REPOSITÓRIOS (Repository - POO)│ │ ENTIDADES DE DOMÍNIO (Domain POO)│
│       app/repositories/          │ │        app/domain/entities/      │
├──────────────────────────────────┤ ├──────────────────────────────────┤
│ - class UsuarioRepository        │ │ - class Usuario                  │
│ - class EnderecoRepository       │ │   * Encapsulamento (_senha_hash) │
│ - Injeção de pymysql.Connection  │ │   * Composição (self.endereco)   │
│ - Consultas com %s parametrizado │ │   * Regras de negócio e máscaras │
│ - Mapeamento row -> Entidade     │ │ - class Endereco                 │
└───────────────────┬──────────────┘ └──────────────────────────────────┘
                    │
                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                 BANCO DE DADOS RELACIONAL (MySQL / TiDB)               │
│                   Tabelas: Usuarios | Endereco                         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Modelagem Direta de Domínio (`app/domain/entities/`)

Em estrita consonância com a decisão de projeto, **não foi criada uma classe intermediária artificial `Pessoa`**, pois o banco de dados possui apenas as tabelas `Usuarios` e `Endereco`. A modelagem focou no princípio clássico:
> *"Favoreça a Composição em relação à Herança (Composition over Inheritance)."*

### 2.1. Entidade `Usuario` ([`app/domain/entities/usuario.py`](file:///c:/Users/israe/Documents/ESTUDOS%20PROGRAMA%C3%87%C3%83O%20WEB/projeto-grau-tec/ello-mineiro-mvp/app/domain/entities/usuario.py))

A classe central do sistema representa o usuário institucional, encapsulando credenciais, dados civis e métodos de negócio.

#### Estrutura de Atributos:
* `id: Optional[int]`: Chave primária gerada pelo banco.
* `user_login: str`: Nome de usuário único (preserva maiúsculas/minúsculas).
* `email: str`: E-mail único formatado em minúsculas.
* `_senha_hash: str` (**Privado / Encapsulado**): Armazena o hash Argon2id. O atributo possui prefixo `_` e **nunca é exportado em dicionários ou respostas da API**.
* `nome: str`: Nome completo civil.
* `genero: Optional[str]`: Gênero autodeclarado (opcional).
* `cpf: str`: Cadastro de Pessoa Física limpo (11 dígitos numéricos).
* `rg: str`: Registro Geral limpo e em maiúsculas.
* `data_nasc: Optional[date]`: Data de nascimento (convertida defensivamente).
* `telefone: Optional[str]` e `telefone_sec: Optional[str]`: Telefones com DDD apenas dígitos.
* `permissao_nome: str`: Perfil no sistema (padrão `'Usuario'`).
* `ativo: bool`: Flag de exclusão lógica (soft delete).
* `endereco: Optional[Endereco]` (**Composição**): Referência interna à entidade de endereço.

#### Métodos de Negócio e Encapsulamento:
1. **`verificar_senha(self, senha_pura: str) -> bool`:**
   Delega a validação criptográfica à própria entidade. Compara a senha em texto puro contra `self._senha_hash` via Argon2id sem expor o hash para fora da classe.
2. **`vincular_endereco(self, endereco: Endereco) -> None`:**
   Executa a Composição de objetos no domínio. Valida que o objeto recebido é uma instância válida de `Endereco` e atualiza a amarração bidirecional.
3. **`atualizar_senha_hash(self, novo_hash: str) -> None`:**
   Altera a senha de forma controlada após validações de pré-requisitos.
4. **`obter_nome_formatado(self) -> str`:**
   Retorna o nome formatado em *Title Case* inteligente, preservando preposições da língua portuguesa em minúsculas (`da`, `de`, `do`, `das`, `dos`, `e`). Exemplo: `carlos da silva` vira `Carlos da Silva`.
5. **`obter_cpf_mascarado(self) -> str`:**
   Retorna o CPF mascarado para exibição segura em telas públicas (`123.***.***-01`), preservando a LGPD.
6. **`obter_rg_mascarado(self) -> str`:**
   Retorna o RG mascarado para proteção de privacidade (`MG.***-8`).
7. **`desativar(self) -> None` e `ativar(self) -> None`:**
   Controla o estado de ativação da conta (RN03 - exclusão lógica).
8. **`to_dict(self, incluir_privados: bool = False) -> Dict[str, Any]`:**
   Serializa os dados da entidade em formato de dicionário puro. Por segurança estrita, `_senha_hash` só é incluída se `incluir_privados=True` for solicitado explicitamente (como na rotina de login).

---

### 2.2. Entidade `Endereco` ([`app/domain/entities/endereco.py`](file:///c:/Users/israe/Documents/ESTUDOS%20PROGRAMA%C3%87%C3%83O%20WEB/projeto-grau-tec/ello-mineiro-mvp/app/domain/entities/endereco.py))

Modela a localização geográfica e residencial do usuário.

#### Estrutura de Atributos:
* `id: Optional[int]`: Identificador do registro na tabela `Endereco`.
* `usuario_id: Optional[int]`: Chave estrangeira que referencia o titular.
* `tipo: str`: Tipo do logradouro (padrão `'Residencial'`).
* `cep: str`: CEP limpo (8 dígitos numéricos).
* `rua: str`, `numero: str`, `bairro: str`, `cidade: str`, `uf: str`.
* `complemento: Optional[str]`: Informação complementar do imóvel.
* `situacao: str`: Situação cadastral (padrão `'ATIVO'`).

#### Métodos de Negócio:
1. **`formatar_cep(self) -> str`:**
   Retorna o CEP com máscara visual padrão dos Correios (`30110-000`).
2. **`obter_endereco_completo(self) -> str`:**
   Retorna a linha única formatada para correspondências e etiquetas (ex: `"Rua Mato Grosso, 142, Apto 201 - Belvedere, Belo Horizonte/MG - CEP: 30110-000"`).
3. **`to_dict(self) -> Dict[str, Any]`:**
   Converte os atributos da entidade em dicionário compatível com os esquemas Pydantic da API.

---

## 3. Padrão Repositório em Classes (`app/repositories/`)

Os repositórios foram convertidos em classes com **injeção de dependência** da conexão `pymysql.Connection` através de seu construtor `__init__`.

### 3.1. `UsuarioRepository` ([`app/repositories/usuario_repository.py`](file:///c:/Users/israe/Documents/ESTUDOS%20PROGRAMA%C3%87%C3%83O%20WEB/projeto-grau-tec/ello-mineiro-mvp/app/repositories/usuario_repository.py))
* **`salvar(usuario: Usuario) -> int`:** Insere o registro na tabela `Usuarios` usando SQL parametrizado (`%s`) e injeta no próprio objeto o ID gerado pelo banco (`usuario.id = lastrowid`).
* **`buscar_para_autenticacao(identificador: str) -> Optional[Usuario]`:** Busca por `user_login` ou `email` e hidrata o resultado em uma instância de `Usuario` (incluindo o hash privado para conferência).
* **`buscar_por_id(usuario_id: int) -> Optional[Usuario]`:** Recupera os dados civis e de perfil do usuário.
* **`verificar_conflito_unicidade(...) -> Optional[str]`:** Valida se já existe duplicidade de `user_login`, `email`, `cpf` ou `rg`.
* **`_mapear_linha_para_entidade(row: dict) -> Usuario`:** Método auxiliar interno (*mapper*) responsável por transformar o dicionário cru retornado pelo driver PyMySQL em uma entidade `Usuario`.

### 3.2. `EnderecoRepository` ([`app/repositories/endereco_repository.py`](file:///c:/Users/israe/Documents/ESTUDOS%20PROGRAMA%C3%87%C3%83O%20WEB/projeto-grau-tec/ello-mineiro-mvp/app/repositories/endereco_repository.py))
* **`salvar(endereco: Endereco) -> int`:** Insere o endereço vinculado ao `usuario_id` e atribui o ID gerado ao objeto.
* **`buscar_por_usuario_id(usuario_id: int) -> Optional[Endereco]`:** Retorna o endereço ativo do usuário como instância da classe `Endereco`.
* **`listar_por_usuario(usuario_id: int) -> List[Endereco]`:** Retorna lista de instâncias `Endereco` ativas.

### 3.3. Fachada de Retrocompatibilidade (`usuarios.py` e `enderecos.py`)
Para manter a compatibilidade com qualquer chamada existente sem quebra de código legado, os arquivos `app/repositories/usuarios.py` e `app/repositories/enderecos.py` foram mantidos como fachadas (*facade*), instanciando internamente `UsuarioRepository` e `EnderecoRepository` e repassando as chamadas.

---

## 4. Camada de Serviços: `AuthService` (`app/services/`)

A classe [`AuthService`](file:///c:/Users/israe/Documents/ESTUDOS%20PROGRAMA%C3%87%C3%83O%20WEB/projeto-grau-tec/ello-mineiro-mvp/app/services/auth_service.py) centraliza toda a inteligência de processos e controle transacional:

### Fluxo Atômico de Cadastro (`cadastrar_usuario`):
1. **Validação de Unicidade:** Consulta `UsuarioRepository.verificar_conflito_unicidade`. Se houver choque, levanta `HTTPException(409 Conflict)`.
2. **Criptografia:** Gera o hash da senha em Argon2id via `gerar_hash_senha`.
3. **Instanciação e Composição:** Cria a instância de `Usuario` e a instância de `Endereco`, invocando `usuario.vincular_endereco(endereco)`.
4. **Transação Atômica (ACID - Tudo ou Nada):**
   ```python
   try:
       novo_usuario_id = self.usuario_repo.salvar(usuario_entidade)
       endereco_entidade.usuario_id = novo_usuario_id
       self.endereco_repo.salvar(endereco_entidade)
       self.conn.commit()  # Confirmação atômica
       return usuario_entidade
   except Exception:
       self.conn.rollback()  # Reversão total em caso de qualquer falha
       raise HTTPException(500, detail="Ocorreu um erro ao salvar o cadastro...")
   ```
   **Garantia Arquitetural:** Isso impede matematicamente que um endereço fique órfão sem usuário ou que um usuário seja criado sem endereço vinculado.

### Fluxo de Autenticação Segura (`autenticar`):
1. Busca o usuário por `identificador` (login ou e-mail).
2. Valida se a conta está ativa (`usuario.ativo`).
3. Invoca o método encapsulado da entidade: `usuario.verificar_senha(senha_pura)`.
4. Caso as credenciais sejam incorretas, emite mensagem genérica com `HTTP 401 Unauthorized` para mitigar ataques de enumeração de contas (RNF07 / RNF10).

---

## 5. Roteadores e Injeção de Dependências

Os controladores HTTP FastAPI tornaram-se classes consumidoras enxutas:

* **[`app/routers/auth.py`](file:///c:/Users/israe/Documents/ESTUDOS%20PROGRAMA%C3%87%C3%83O%20WEB/projeto-grau-tec/ello-mineiro-mvp/app/routers/auth.py):**
  * Rota `POST /api/auth/register`: Injeta a conexão do banco via `Depends(get_db)`, instancia `AuthService(conn)` e delega a criação. Retorna o JSON padronizado.
  * Rota `POST /api/auth/login`: Invoca `AuthService(conn).autenticar(dados.identificador, dados.senha)`, gera o token JWT e anexa o cookie seguro `HttpOnly`.
* **[`app/routers/me.py`](file:///c:/Users/israe/Documents/ESTUDOS%20PROGRAMA%C3%87%C3%83O%20WEB/projeto-grau-tec/ello-mineiro-mvp/app/routers/me.py):**
  * Rota `GET /api/me`: Invoca `AuthService(conn).obter_usuario_com_endereco(usuario["id"])` e retorna os dados agregados para o dashboard (`home.html`).
* **[`app/dependencies.py`](file:///c:/Users/israe/Documents/ESTUDOS%20PROGRAMA%C3%87%C3%83O%20WEB/projeto-grau-tec/ello-mineiro-mvp/app/dependencies.py):**
  * `get_current_user`: Decodifica o cookie `access_token` e utiliza `UsuarioRepository(conn).buscar_por_id(usuario_id)` para validar a sessão.

---

## 6. Guia Prático para Futuras Análises, Correções e Extensões

Caso a equipe precise estender o sistema após o MVP, siga este roteiro padronizado:

### 6.1. Como Adicionar um Novo Atributo ao Usuário
1. **Banco de Dados:** Adicione a coluna via `ALTER TABLE Usuarios ADD COLUMN ...;` no banco.
2. **Entidade de Domínio:** Atualize `Usuario.__init__` em [`app/domain/entities/usuario.py`](file:///c:/Users/israe/Documents/ESTUDOS%20PROGRAMA%C3%87%C3%83O%20WEB/projeto-grau-tec/ello-mineiro-mvp/app/domain/entities/usuario.py) e o método `to_dict()`.
3. **Repositório:** Inclua o campo nas queries SQL de `salvar`, `buscar_por_id` e no método `_mapear_linha_para_entidade` de [`app/repositories/usuario_repository.py`](file:///c:/Users/israe/Documents/ESTUDOS%20PROGRAMA%C3%87%C3%83O%20WEB/projeto-grau-tec/ello-mineiro-mvp/app/repositories/usuario_repository.py).
4. **Schemas e Validação:** Atualize os modelos Pydantic em [`app/schemas.py`](file:///c:/Users/israe/Documents/ESTUDOS%20PROGRAMA%C3%87%C3%83O%20WEB/projeto-grau-tec/ello-mineiro-mvp/app/schemas.py).

### 6.2. Como Adicionar uma Nova Entidade (ex: `Turma` ou `Matricula`)
1. Crie o arquivo da classe de domínio pura em `app/domain/entities/turma.py`.
2. Crie a classe de repositório com injeção de conexão em `app/repositories/turma_repository.py`.
3. Se envolver lógica de negócio ou transações complexas, crie o serviço correspondente em `app/services/turma_service.py`.
4. Crie o roteador FastAPI em `app/routers/turmas.py` injetando o serviço.

### 6.3. Como Rodar e Validar os Testes
Sempre que fizer qualquer alteração no backend, execute no terminal da raiz do projeto:
```powershell
.venv\Scripts\python test_api.py
```
O teste valida automaticamente 11 cenários críticos: saúde da API, proteção de mutabilidade com `X-API-Key`, preenchimento de campos opcionais nulos, integridade atômica com endereço obrigatório, validação de duplicidade (409), emissão de cookies de sessão e proteção contra ataques por força bruta (Rate Limiting 429).
