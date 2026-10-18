# Escola Particular Ello Mineiro — MVP

Repositório do MVP (Produto Mínimo Viável) do sistema de gestão escolar da **Escola Particular Ello Mineiro**, desenvolvido como trabalho em grupo da disciplina de **Banco de Dados**.

A visão do sistema é centralizar a autenticação dos usuários para que, nas próximas fases, alunos consultem notas e frequência, professores façam os lançamentos acadêmicos e as equipes administrativa e de suporte gerenciem a plataforma. **Esta primeira fase cobre apenas cadastro e login**, com foco em segurança.

> **Status:** Backend implementado e testado com sucesso localmente. Próxima etapa: desenvolvimento da interface web. Veja a pasta [`docs/`](docs/).

---

## Como Executar Localmente

### 1. Pré-requisitos
* **Python 3.10+** instalado.
* **MySQL** ativo (via **XAMPP**, Docker ou serviço local) com o script [`database/seed.sql`](database/seed.sql) executado no banco `ello_mineiro`.
* Arquivo `.env` configurado na raiz com as credenciais do banco (use [`.env.example`](.env.example) como base).

### 2. Preparação do Ambiente Virtual (venv)

#### Criar o ambiente virtual (apenas na primeira vez):
```bash
python -m venv .venv
```

#### Ativar o ambiente virtual:
* **No Windows (PowerShell):**
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
  *(Se o PowerShell bloquear a execução de scripts, execute uma vez como Administrador: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`)*

* **No Windows (Prompt de Comando / CMD):**
  ```cmd
  .\.venv\Scripts\activate.bat
  ```

* **No Linux ou macOS (Bash / Zsh):**
  ```bash
  source .venv/bin/activate
  ```

> 💡 **Dica:** Quando a venv estiver ativa, o início da linha do terminal exibirá o prefixo `(.venv)`. A partir daí, você pode usar os comandos normais (`pip`, `python`, `uvicorn`) sem precisar referenciar o caminho completo da pasta!

#### Instalar as dependências:
```bash
pip install -r requirements.txt
```

---

### 3. Inicialização do Backend
Com a venv ativa:
```bash
uvicorn app.main:app --reload
```
O servidor estará rodando em: **`http://localhost:8000`**

---

### 4. Documentação Interativa da API (Swagger & Postman)
Com o servidor rodando, acesse no navegador:
* **Swagger UI:** [`http://localhost:8000/docs`](http://localhost:8000/docs)
* **ReDoc alternativo:** [`http://localhost:8000/redoc`](http://localhost:8000/redoc)
* **Postman Collection pronta:** Você pode importar diretamente o arquivo oficial [`docs/ello_mineiro_postman_collection.json`](docs/ello_mineiro_postman_collection.json) no Postman para ter todas as rotas e payloads de exemplo pré-configurados!

Permite testar visualmente todas as rotas de cadastro, login, logout e `/me` diretamente pela interface.

---

### 5. Teste de Integridade e Saúde da API
Para verificar se a API está online e se a conexão com o banco MySQL está funcionando:
* **Pelo navegador:** [`http://localhost:8000/health`](http://localhost:8000/health)
* **Retorno esperado:**
  ```json
  {
    "status": "online",
    "banco": "conectado",
    "db_check": true
  }
  ```

---

### 6. Execução da Bateria de Testes Automatizados
Com a venv ativa, execute o script de validação de ponta a ponta que testa automaticamente o health check, cadastro com perfil fixo, detecção de duplicidade (409), login, cookie HttpOnly e `/me`:
```bash
python test_api.py
```

*(Para desativar o ambiente virtual quando terminar de trabalhar, basta digitar `deactivate` no terminal).*

---

## Escopo da Fase 1

| Dentro | Fora (fases futuras) |
|---|---|
| Cadastro público de usuários | Promoção de perfil pelo setor administrativo |
| Login com `user_login` ou e-mail + senha | Matrícula do aluno e registro funcional |
| Tela Home pós-login | Turmas, notas, presença, matérias, calendário |
| Armazenamento seguro de senhas | — |

Todo usuário cadastrado recebe o perfil padrão **`Usuario`**. Os perfis `Aluno`, `Professor`, `Suporte` e `Administrativo` já existem no banco, mas só serão atribuídos no futuro pelo setor administrativo ([regras futuras](docs/03-regras-futuras.md)).

### Front-end (estático)
HTML, CSS e JavaScript servidos pelo próprio backend, consumindo a API em `/api/*` com URLs relativas.
* **Login (`/`):** autenticação com `user_login` (nome de usuário) **ou** e-mail e senha.
* **Cadastro (`/cadastro`):** formulário de novos usuários. **Não há escolha de perfil.**
* **Home (`/home`):** página exibida após o login; os dados vêm de `GET /api/me`.

### Backend e API
| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/auth/register` | Cria o usuário com o perfil `Usuario` |
| POST | `/api/auth/login` | Valida credenciais e grava o JWT em cookie `HttpOnly` |
| POST | `/api/auth/logout` | Apaga o cookie de sessão |
| GET | `/api/me` | Dados do usuário logado (sem a senha) |
| GET | `/health` | Verifica se a aplicação está no ar |

Contrato completo em [docs/01-requisitos.md](docs/01-requisitos.md).

### Segurança
* Senhas guardadas apenas como hash **Argon2id** ou **bcrypt**; nunca em texto puro.
* JWT (HS256, expiração curta) em cookie **`HttpOnly; Secure; SameSite=Lax`**: o JavaScript não acessa o token.
* Proteção contra CSRF (`SameSite`, `POST` só com JSON, checagem de `Origin`).
* SQL sempre parametrizado (prevenção de SQL Injection).
* Segredos em variáveis de ambiente; front e API na mesma origem (sem CORS).
* Dados pessoais (CPF, RG) tratados conforme a LGPD.

### Banco de dados (MySQL)
Esquema em [`database/seed.sql`](database/seed.sql):
* **`Permissoes`:** perfis fixos (`Usuario`, `Aluno`, `Professor`, `Suporte`, `Administrativo`).
* **`Usuarios`:** credenciais (`user_login`, e-mail, `senha_hash`), perfil e dados pessoais.
* **`Endereco`:** endereços do usuário (relacionamento 1:N).

---

## Tecnologias

| Camada | Escolha |
|---|---|
| Front-end | HTML5, CSS3, JavaScript (Fetch API) |
| Backend | Python + **FastAPI** (Swagger automático em `/docs`) |
| Acesso ao banco | **SQL puro** com PyMySQL (sem ORM), concentrado em `app/repositories/` |
| Banco | **MySQL** (TiDB Cloud Serverless) |
| Segurança | `argon2-cffi` ou `bcrypt` (hash) e PyJWT (token) |
| Hospedagem | **Render**: deploy único, front e API na mesma URL |

---

## Estrutura do repositório

```
app/          código FastAPI (main.py, db.py, repositories/, routers/)
database/     seed.sql (esquema do banco)
frontend/     index.html, cadastro.html, home.html, static/, test/ (protótipos)
docs/         requisitos, decisões de arquitetura e regras futuras
```

## Documentação

1. [Contexto e ponto de retomada](docs/00-contexto-handoff.md)
2. [Requisitos](docs/01-requisitos.md)
3. [Decisões de arquitetura](docs/02-decisoes-arquitetura.md)
4. [Regras de negócio futuras](docs/03-regras-futuras.md)
5. [Guia de ambiente e execução](docs/04-guia-execucao-e-ambiente.md)
6. [Modelagem e especificação do front-end](docs/05-modelagem-frontend.md)
7. [Quadro Kanban de Acompanhamento (Obsidian)](docs/kanban.md)

