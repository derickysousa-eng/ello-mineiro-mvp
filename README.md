# Escola Particular Ello Mineiro — MVP

Repositório oficial do MVP (Produto Mínimo Viável) do sistema de gestão escolar da **Escola Particular Ello Mineiro**, desenvolvido como trabalho em grupo da disciplina de **Banco de Dados / Desenvolvimento Web**.

A visão da plataforma é centralizar a gestão e autenticação acadêmica com foco em segurança, integridade relacional e experiência do usuário. **Esta primeira fase cobre o fluxo completo de cadastro institucional e login seguro**, preparando a base para as fases futuras de lançamento de notas, presença e gestão escolar.

link produção: https://ello-mineiro-mvp.onrender.com/

---

## 🚀 Status do Projeto e Deploy em Produção

* **Status Atual:** ✅ **100% OPERACIONAL E EM PRODUÇÃO ATIVA**.
* **Hospedagem da Aplicação (Full-Stack PaaS):** [Render](https://render.com) — Contêiner Linux executando FastAPI + Uvicorn na mesma origem (*Same-Origin Architecture*).
* **Banco de Dados em Nuvem (DBaaS):** [TiDB Cloud Serverless](https://tidbcloud.com) — Banco Relacional Distribuído NewSQL compatível com MySQL 8.0, sediado na AWS (região `us-east-1` / N. Virginia) com criptografia obrigatória ponta a ponta via **TLS/SSL** (`DB_SSL=true`).
* **Segurança de Variáveis de Ambiente:** Totalmente aderente ao padrão **12-Factor App** — zero credenciais expostas no código (*hardcoded*), com segredos gerenciados via variáveis de ambiente criptografadas no painel do Render e arquivo `.env` protegido localmente pelo `.gitignore`.

---

## 🛠️ Tecnologias Utilizadas

### Backend e API
* **Linguagem & Servidor:** **Python 3.10+** com servidor ASGI de alta performance **Uvicorn**.
* **Framework:** **FastAPI** — Criação de rotas RESTful assíncronas, documentação interativa automática (Swagger/OpenAPI em `/docs` e ReDoc em `/redoc`).
* **Validação de Dados e Contratos:** **Pydantic v2** — Validações estritas de tipos, contratos de requisição/resposta e recálculo do algoritmo oficial do Módulo 11 de CPF.
* **Acesso ao Banco de Dados:** **SQL Puro com PyMySQL** — Queries 100% parametrizadas (proteção absoluta contra SQL Injection), sem ORMs pesados, demonstrando domínio pleno da linguagem SQL.
* **Segurança e Criptografia:**
  * **Argon2id (`argon2-cffi`):** Hashing de senhas resistente a ataques de força bruta com hardware especializado (GPUs/ASICs).
  * **PyJWT:** Assinatura digital de tokens de sessão com algoritmo HMAC-SHA256.
  * **Cookies HttpOnly:** Entrega de token via cookie seguro (`HttpOnly; Secure; SameSite=Lax`), tornando o sistema imune a roubo de sessão via ataques XSS (*Cross-Site Scripting*).
  * **Rate Limiting por IP (`RNF07`):** Limitador de taxa em memória por janela deslizante (*Sliding Window*) com resposta `HTTP 429 Too Many Requests`.
  * **Guarda de Mutabilidade (`X-API-Key` + *Same-Origin*):** Autorização transparente para navegação no site oficial e exigência de chave privada para clientes externos/robôs (`HTTP 403 Forbidden`).

### Front-end e Experiência do Usuário (UI/UX)
* **Arquitetura Vanilla:** **HTML5 Semântico**, **CSS3 Moderno** e **JavaScript ES6+ Nativo** servidos diretamente pelo backend (`GET /`, `GET /cadastro`, `GET /home`, `GET /recuperacao`), eliminando complexidade e custos de CORS.
* **Design System Institucional:** Folha de estilos centralizada ([frontend/static/css/style.css](frontend/static/css/style.css)) com variáveis CSS (`:root`), paleta em Azul Marinho Real (`#1A365D`) e Dourado Nobre (`#CFAD6D`).
* **Iconografia Profissional:** Biblioteca **Bootstrap Icons** via CDN (iconografia vetorial 100% SVG, sem uso de emojis informais).
* **Lógica Inteligente do Cliente ([frontend/static/js/auth.js](frontend/static/js/auth.js)):**
  * **Title Case Automático:** Converte nomes próprios capitalizando iniciais e preservando preposições em minúsculas (`da`, `de`, `do`, `dos`, `das`, `e`).
  * **Máscaras Dinâmicas:** Formatação adaptativa em tempo real para CPF, RG flexível (7 a 13 dígitos) e telefones (fixo de 10 dígitos vs. celular de 11 dígitos).
  * **Medidor de Força de Senha:** Cálculo de entropia e validação visual de requisitos de segurança.
  * **Route Guard no Dashboard ([frontend/static/js/home.js](frontend/static/js/home.js)):** Validação ativa de sessão chamando `GET /api/me` e mascaramento de dados sensíveis na tela com asteriscos centrais para preservar a privacidade do aluno.

### APIs e Serviços Externos
* **ViaCEP (Webservice dos Correios):** Integração assíncrona que autocompleta automaticamente Rua, Bairro, Cidade e Estado ao digitar o 8º dígito do CEP, acompanhada de mecanismo de contingência para liberação manual imediata caso o serviço oscile.

---

## 🌿 Estratégia de Branches e Evolução Arquitetural

Adotamos o fluxo de desenvolvimento profissional com segregação de fases via Git:

* **Branch `main` (Versão 1 — MVP Estável em Produção):**
  * Contém a aplicação consolidada em produção ativa no Render e TiDB Cloud.
  * Backend estruturado com repositórios SQL puros, POO aplicada em schemas/validadores Pydantic e rate limiting.
* **Branch `feature/refatoracao-poo` (Versão 2 — Orientação a Objetos Avançada):**
  * Branch planejada para os ajustes finos de **Programação Orientada a Objetos (POO)** exigidos pela disciplina.
  * Introdução de entidades de domínio diretas (`class Usuario` e `class Endereco`), priorizando o princípio de **Composição sobre Herança** (`Usuario` compondo `Endereco`), **Abstração Direta** (mapeamento 1:1 com o banco) e **Encapsulamento** rigoroso de métodos de negócio (`verificar_senha()`, formatações e mascaramentos), acompanhadas de classes de serviço (`AuthService`) e repositórios orientados a objetos.
  * Todo o planejamento técnico desta migração encontra-se detalhado em [docs/07-planejamento-refatoracao-poo.md](docs/07-planejamento-refatoracao-poo.md).

---

## 💻 Como Executar o Projeto Localmente

### 1. Pré-requisitos
* **Python 3.10+** instalado.
* Conexão ativa com o banco MySQL local ou string remota do **TiDB Cloud**.
* Arquivo `.env` configurado na raiz com base no [`.env.example`](.env.example).

### 2. Preparação do Ambiente Virtual (venv)

```bash
# 1. Criar o ambiente virtual
python -m venv .venv

# 2. Ativar o ambiente virtual:
# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# Windows (CMD):
.\.venv\Scripts\activate.bat
# Linux/macOS:
source .venv/bin/activate

# 3. Instalar as dependências do projeto
pip install -r requirements.txt
```

### 3. Inicialização do Servidor Local
```bash
uvicorn app.main:app --reload
```
A aplicação estará disponível em: **`http://localhost:8000`**

### 4. Documentação Interativa da API
Com o servidor rodando, acesse:
* **Swagger UI:** [`http://localhost:8000/docs`](http://localhost:8000/docs)
* **ReDoc:** [`http://localhost:8000/redoc`](http://localhost:8000/redoc)
* **Postman Collection:** Importe o arquivo [`docs/ello_mineiro_postman_collection.json`](docs/ello_mineiro_postman_collection.json) com todos os payloads e autenticação pré-configurados.

### 5. Execução da Bateria de Testes Automatizados
```bash
# Executa os 11 cenários de testes de segurança, integridade e negócio
python test_api.py
```

---

## 🗄️ Estrutura do Banco de Dados Relacional (MySQL / TiDB Cloud)

O esquema oficial encontra-se em [`database/seed.sql`](database/seed.sql):
* **`Permissoes`:** Perfis fixos de acesso (`Usuario`, `Aluno`, `Professor`, `Suporte`, `Administrativo`).
* **`Usuarios`:** Credenciais (`user_login`, `email`, `senha_hash`), perfil atribuído e dados civis obrigatórios (`cpf`, `rg`).
* **`Endereco`:** Endereço residencial atrelado ao usuário em transação atômica (`usuario_id` com `ON DELETE CASCADE`).

---

## 📚 Documentação Técnica Completa

### Engenharia de Software e Especificações (`docs/`)
1. [00-contexto-handoff.md](docs/00-contexto-handoff.md) — Passagem de bastão, status atual e arquitetura geral.
2. [01-requisitos.md](docs/01-requisitos.md) — Requisitos funcionais (RF), não funcionais (RNF) e regras de negócio (RN).
3. [02-decisoes-arquitetura.md](docs/02-decisoes-arquitetura.md) — Decisões de stack, deploy único e SQL puro.
4. [03-regras-futuras.md](docs/03-regras-futuras.md) — Regras para fases pós-MVP (matrículas, turmas, notas).
5. [04-guia-execucao-e-ambiente.md](docs/04-guia-execucao-e-ambiente.md) — Guia do XAMPP, DBeaver, `.env` e pipeline.
6. [05-modelagem-frontend.md](docs/05-modelagem-frontend.md) — Especificação detalhada da interface web e componentes.
7. [06-arquitetura-servidor-e-rotas.md](docs/06-arquitetura-servidor-e-rotas.md) — Lógica do `main.py`, rotas estáticas e centralização CSS.
8. [07-planejamento-refatoracao-poo.md](docs/07-planejamento-refatoracao-poo.md) — Planejamento técnico da refatoração para POO na branch `feature/refatoracao-poo`.
9. [kanban.md](docs/kanban.md) — Quadro Kanban oficial de acompanhamento de tarefas.

### Caderno de Apresentação e Demonstração Acadêmica (`docs-apresentacao/`)
1. [apresentacao-frontend.md](docs-apresentacao/apresentacao-frontend.md) — Interface, UX, bibliotecas e integração ViaCEP.
2. [apresentacao-backend-e-banco.md](docs-apresentacao/apresentacao-backend-e-banco.md) — Arquitetura FastAPI, CRUD, SQL puro e transações atômicas.
3. [infraestrutura-e-seguranca.md](docs-apresentacao/infraestrutura-e-seguranca.md) — Topologia Render + TiDB Cloud, 12-Factor App e segurança em camadas.
4. [algoritmo-validacao-cpf.md](docs-apresentacao/algoritmo-validacao-cpf.md) — Fundamentação matemática do Módulo 11 e legislação da Receita Federal.
5. [guia-cadastro-usuario-guiado.md](docs-apresentacao/guia-cadastro-usuario-guiado.md) — Roteiro de demonstração ao vivo com geradores sintéticos da 4Devs.
