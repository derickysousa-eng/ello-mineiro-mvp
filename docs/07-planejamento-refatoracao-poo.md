# Planejamento da Refatoração para Programação Orientada a Objetos (POO) — Versão 2

> **Documento:** `docs/07-planejamento-refatoracao-poo.md`  
> **Finalidade:** Especificação arquitetural e guia de implementação da transição do backend para Programação Orientada a Objetos sólida, a ser desenvolvida na branch `feature/refatoracao-poo`.  
> **Alinhamento Acadêmico:** Atendimento rigoroso aos critérios da **Fase 2 (Desenvolvimento — POO em Python)** definidos pela disciplina.

---

## 1. Contexto e Justificativa da Evolução

A **Versão 1 (MVP Atual na branch `main`)** atingiu 100% de estabilidade:
* O sistema está em produção ativa no **Render** conectado ao **TiDB Cloud**.
* O banco de dados relacional foi homologado com SQL puro (`PyMySQL`) e transações atômicas.
* Todas as rotas RESTful e a interface web operam na mesma origem (*Same-Origin*).

Embora a V1 já utilize POO de forma implícita (via classes `BaseModel` do Pydantic em [schemas.py](file:///c:/Users/israe/Documents/ESTUDOS%20PROGRAMA%C3%87%C3%83O%20WEB/projeto-grau-tec/ello-mineiro-mvp/app/schemas.py) e na classe `InMemoryRateLimiter` em [security_guards.py](file:///c:/Users/israe/Documents/ESTUDOS%20PROGRAMA%C3%87%C3%83O%20WEB/projeto-grau-tec/ello-mineiro-mvp/app/security_guards.py)), a camada de repositórios e serviços foi estruturada em módulos funcionais.

A **Versão 2 (Branch `feature/refatoracao-poo`)** elevará a qualidade de código do projeto através de uma **Modelagem de Domínio Orientada a Objetos**, aplicando formalmente os 4 pilares fundamentais da POO sem quebrar o contrato da API nem alterar a interface visual.

---

## 2. Modelagem Direta de Domínio (Abstração, Encapsulamento e Composição)

Seguindo o princípio clássico de engenharia de software **KISS (*Keep It Simple, Stupid*)** e o padrão consagrado da literatura (*Gang of Four*): **"Favoreça a Composição em relação à Herança"**, o domínio mapeia de forma direta, clara e sem complexidade desnecessária as entidades do banco de dados:

```
┌───────────────────────────────────────────────┐
│                 class Usuario                 │
├───────────────────────────────────────────────┤
│ + id: Optional[int]                           │
│ + user_login: str                             │
│ + email: str                                  │
│ - _senha_hash: str      [ENCAPSULAMENTO]      │
│ + nome: str                                   │
│ + genero: Optional[str]                       │
│ + cpf: str                                    │
│ + rg: str                                     │
│ + data_nasc: Optional[date]                   │
│ + telefone: Optional[str]                     │
│ + telefone_sec: Optional[str]                 │
│ + permissao_nome: str                         │
│ + ativo: bool                                 │
│ + endereco: Endereco    [COMPOSIÇÃO] ─────────┼─────┐
├───────────────────────────────────────────────┤     │
│ + verificar_senha(senha_pura: str) -> bool    │     │
│ + obter_nome_formatado() -> str               │     │
│ + obter_cpf_mascarado() -> str                │     │
│ + desativar()                                 │     │
└───────────────────────────────────────────────┘     │
                                                      ▼
                       ┌───────────────────────────────────────────────┐
                       │                class Endereco                 │
                       ├───────────────────────────────────────────────┤
                       │ + id: Optional[int]                           │
                       │ + usuario_id: Optional[int]                   │
                       │ + tipo: str                                   │
                       │ + cep: str                                    │
                       │ + rua: str                                    │
                       │ + numero: str                                 │
                       │ + bairro: str                                 │
                       │ + complemento: Optional[str]                  │
                       │ + cidade: str                                 │
                       │ + uf: str                                     │
                       │ + situacao: str                               │
                       ├───────────────────────────────────────────────┤
                       │ + formatar_cep() -> str                       │
                       │ + obter_endereco_completo() -> str            │
                       └───────────────────────────────────────────────┘
```

### 2.1. Abstração Direta (Mapeamento 1:1 com o Banco)
* **`class Usuario`:** Representa a entidade central do sistema escolar, encapsulando tanto as credenciais de autenticação quanto os dados pessoais civis.
* **`class Endereco`:** Representa o domicílio físico do usuário.

### 2.2. Composição Elegante (*Composition over Inheritance*)
* No banco de dados, `Endereco` possui chave estrangeira para `Usuarios`.
* Na Programação Orientada a Objetos, essa relação se traduz perfeitamente por **Composição**: uma instância de `Usuario` contém internamente uma instância de `Endereco` (`self.endereco = endereco`).
* O objeto `Usuario` coordena e garante que não exista usuário sem endereço vinculado.

### 2.3. Encapsulamento Rigoroso
* O atributo de hash de senha é estritamente privado (`_senha_hash`), impedindo que senhas em texto puro sejam lidas ou vazadas acidentalmente.
* A validação de senha é um método interno da entidade:
  ```python
  usuario.verificar_senha(senha_pura)
  ```
* Métodos de conveniência de exibição e formatação de texto residem na própria classe, eliminando funções soltas.

---

## 3. Padrões de Projeto (Design Patterns) a Serem Implementados

### 3.1. Repository Pattern em Classes (Orientado a Objetos)
Em vez de funções isoladas em arquivos de repositório, criaremos classes com injeção de dependência da conexão:

```python
class UsuarioRepository:
    def __init__(self, conn: pymysql.Connection):
        self.conn = conn

    def salvar(self, usuario: Usuario) -> int:
        """Persiste a entidade Usuario no banco e retorna o ID gerado."""
        pass

    def buscar_por_login_ou_email(self, identificador: str) -> Optional[Usuario]:
        """Recupera do banco e reconstrói o objeto Usuario completo."""
        pass
```

### 3.2. Service Layer (Camada de Serviços de Negócio)
Criaremos a classe `AuthService` para orquestrar as operações de autenticação e registro, mantendo os roteadores do FastAPI limpos e focados apenas em receber a requisição HTTP e retornar o JSON:

```python
class AuthService:
    def __init__(self, usuario_repo: UsuarioRepository, endereco_repo: EnderecoRepository):
        self.usuario_repo = usuario_repo
        self.endereco_repo = endereco_repo

    def cadastrar_novo_usuario(self, dados_registro) -> Usuario:
        # 1. Valida unicidade
        # 2. Instancia objetos Usuario e Endereco
        # 3. Executa transação atômica
        # 4. Retorna a entidade persistida
        pass
```

---

## 4. Nova Estrutura de Pastas do Backend (Branch `feature/refatoracao-poo`)

```
app/
├── domain/                                # [NOVO] Núcleo Orientado a Objetos Puro
│   ├── __init__.py
│   ├── entities/
│   │   ├── usuario.py                     # Classe Usuario de Domínio (Abstração e Encapsulamento)
│   │   └── endereco.py                    # Classe Endereco (Composição)
├── repositories/                          # Repositórios convertidos em Classes
│   ├── usuario_repository.py              # class UsuarioRepository
│   └── endereco_repository.py             # class EnderecoRepository
├── services/                              # [NOVO] Camada de Serviços
│   ├── auth_service.py                    # class AuthService
│   └── session_service.py                 # class SessionService (JWT & Cookies)
├── routers/                               # Controladores Web (FastAPI)
│   ├── auth.py                            # Injeta AuthService
│   └── me.py                              # Consulta AuthService
├── db.py                                  # Conexão e injeção get_db
├── schemas.py                             # Contratos Pydantic v2
├── security.py                            # Utilitários de Hash e Criptografia
└── security_guards.py                     # Rate Limiter e Proteção Mesma Origem
```

---

## 5. Garantia de Qualidade e Critérios de Sucesso

1. **Zero Quebra de Contrato da API:** Os endpoints `/api/auth/register`, `/api/auth/login`, `/api/me` e `/health` manterão exatamente as mesmas entradas e saídas JSON.
2. **Front-end 100% Inalterado:** As páginas HTML, CSS e scripts do navegador continuarão funcionando perfeitamente sem necessidade de modificação.
3. **Bateria de Testes Automatizados:** O script `test_api.py` deverá continuar passando com **11/11 testes aprovados (100% de sucesso)** após a refatoração.
4. **Demonstração para a Banca:** A equipe terá em mãos a comparação visual entre a branch `main` (versão funcional inicial) e a branch `feature/refatoracao-poo` (versão madura em POO com herança, encapsulamento e composição).
