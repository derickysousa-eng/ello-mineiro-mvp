## 1. Projeto

- **O quê:** MVP do sistema de gestão da escola particular **Ello Mineiro**, trabalho em grupo da disciplina de **Banco de Dados** (curso técnico). Projeto de aprendizagem.
- **Escopo da Fase 1:** apenas **cadastro e login** de usuários, com senhas em hash (Argon2id), integridade atômica com endereço obrigatório e rotas de API servidas na mesma origem com cookie `HttpOnly`.
- **Estado atual:** **Backend FastAPI e Front-end Web 100% implementados e integrados** localmente. Bateria de testes automatizados (`test_api.py`) passando com 100% de sucesso. Todas as páginas HTML (`/`, `/cadastro`, `/home`, `/recuperacao`) e ativos estáticos operando na mesma origem, com estilos centralizados em `style.css` e ícones profissionais via Bootstrap Icons.
- **Idioma:** português (documentação, nomes de campos e commits).

## 2. Decisões já consolidadas

| Tema | Decisão |
|---|---|
| Banco | **MySQL** (esquema `database/seed.sql`). Desenvolvido e testado localmente no **XAMPP/DBeaver**; produção futura no **TiDB Cloud Serverless** |
| Backend | **Python + FastAPI**, arquitetura desacoplada em repositórios SQL puros (`PyMySQL`), segurança com **Argon2id** e JWT (`HS256`) |
| Front-end | HTML5 semântico, CSS3 e JavaScript puro (ES6+) **servidos pelo próprio backend** (`GET /` login, `GET /cadastro`, `GET /home` dashboard, `GET /recuperacao`). **Deploy único, mesma origem, sem CORS** |
| Centralização de Estilos | Folha única **`frontend/static/css/style.css`** com variáveis CSS (Design Tokens na paleta `#1A365D` e `#CFAD6D`), garantindo consistência visual e cache rápido no navegador |
| Ícones da Interface | Biblioteca **Bootstrap Icons** via CDN (sem dependência de frameworks ou React, 100% vetorial/SVG, eliminando emojis) |
| Sessão | Cookie **`HttpOnly; Secure; SameSite=Lax; Path=/`** (nome `access_token`). O navegador gerencia de forma transparente sem manipulação direta pelo JS |
| Integridade de Endereço | **Atomicidade total (RN04 / RNF19):** Todo cadastro exige obrigatoriamente um endereço completo. Não existem usuários sem endereço nem endereços órfãos |
| Documentos Pessoais | **CPF e RG Obrigatórios (`NOT NULL` e `UNIQUE`):** Validados estritamente no front-end (módulo 11 em tempo real e regex de RG), no backend (Pydantic com módulo 11) e no banco (`seed.sql`) |
| Perfil no cadastro | Todo usuário nasce com o perfil padrão **`Usuario`**. Perfis avançados (`Aluno`, `Professor`, etc.) existem no banco para o futuro |
| `user_login` | Nome de usuário escolhido pelo usuário (3–30 caracteres, `[a-zA-Z0-9._]`, case preservado no envio e exibição; busca e unicidade case-insensitive no MySQL `utf8mb4_unicode_ci`) |
| Segurança de Mutabilidade | **Chave Privada (`X-API-Key`) + Mesma Origem (RNF18) + Rate Limiting (RNF07):** Mutações externas exigem `X-API-Key` (403 se ausente/inválida); navegação no site oficial opera com zero atrito via mesma origem; Rate Limiter barra abusos com 429 Too Many Requests |

---

## 3. Pontos de Atenção e Funcionalidades Implementadas

### ✅ 3.1. Obrigatoriedade de CPF e RG (`NOT NULL`) — [DECIDIDO E IMPLEMENTADO 100%]:
* **Decisão de Negócio Consolidada:** Por ser um MVP de curso técnico com escopo fechado sem etapa posterior de secretaria física, manter CPF e RG como opcionais deixaria dados vazios em testes e demonstrações acadêmicas.
* **Implementação Realizada em Todas as Camadas:**
  1. **Banco de Dados (`database/seed.sql`):** Atualizado para `cpf CHAR(11) NOT NULL UNIQUE` e `rg VARCHAR(30) NOT NULL UNIQUE`.
  2. **Backend (`app/schemas.py`):** Ambos os campos são obrigatórios no `UsuarioRegisterSchema`. O `cpf` passa por cálculo matemático dos dígitos verificadores pelo algoritmo oficial do **módulo 11**, rejeitando CPFs inválidos ou com sequências repetidas. O `rg` valida a presença de 5 a 14 caracteres alfanuméricos úteis.
  3. **Front-end (`frontend/cadastro.html` e `auth.js`):** Formulário com atributo `required`, máscara dinâmica de RG (7 a 13 dígitos úteis com suporte ao RN e dígito X), cálculo em tempo real do módulo 11 de CPF e bloqueio de submissão caso estejam ausentes ou incorretos.
  4. **Proteção de Privacidade (`home.js`):** No dashboard autenticado, os dados sensíveis de CPF e RG são mascarados com asteriscos centrais para preservar a privacidade do usuário na interface.
  5. **Bateria de Testes (`test_api.py`):** Bateria de testes atualizada para validar a obrigatoriedade (rejeitando com 422 cadastros sem CPF/RG) e homologada com **11/11 testes aprovados**.

### ✅ 3.2. Front-end e Integrações 100% Concluídos:

1. **`frontend/index.html` (Rota `GET /`):** Login com suporte unificado a nome de usuário (`user_login`) ou e-mail (RF05), alternador de visualização de senha com ícones (`bi-eye` / `bi-eye-slash`), spinner de carregamento e link direto para recuperação de senha.
2. **`frontend/cadastro.html` (Rota `GET /cadastro`):** Cadastro completo com Title Case inteligente para nomes (preservando `da, de, do, dos, das, e`), comboboxes padronizados do IBGE para `genero` e estados da federação para `uf`, máscaras dinâmicas adaptativas para telefone (10 dígitos fixo vs 11 dígitos celular), cálculo do algoritmo módulo 11 de CPF em tempo real, integração com ViaCEP (com liberação de edição manual em caso de indisponibilidade) e aceite formal de termos institucionais.
3. **`frontend/home.html` (Rota `GET /home`):** Dashboard acadêmico integrado com Route Guard que valida sessão chamando `GET /api/me`. Exibe dados cadastrais e endereço completo vinculado, além de botão seguro de encerramento de sessão (Logout via `POST /api/auth/logout`).
4. **`frontend/recuperacao.html` (Rota `GET /recuperacao`):** Tela pública com formulário para inserção de e-mail e token de recuperação, com banner informativo do status do recurso no MVP e canal de contato com a secretaria acadêmica.
5. **Centralização e Governança:** Documentada detalhadamente em [docs/06-arquitetura-servidor-e-rotas.md](06-arquitetura-servidor-e-rotas.md).

---

## 4. Próxima Etapa de Execução (Passo 5 — Banco em Nuvem e Deploy)

Com a API, as validações de CPF/RG obrigatórios (`NOT NULL`), o banco local e todo o front-end estático finalizados e testados com 100% de sucesso:
1. **Banco na Nuvem (TiDB Cloud Serverless):** Criação da instância serverless gratuita do TiDB (compatível com MySQL), execução do `database/seed.sql` atualizado e teste de conexão via string remota com SSL obrigatório.
2. **Deploy Único no Render:** Configurar repositório no Render Web Service com variáveis de ambiente (`DB_*`, `JWT_SECRET_KEY`, `API_KEY`) e comando de inicialização `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.


---

## 5. Estrutura do Repositório

```
ello-mineiro-mvp/
├── docs/                                  # Documentação completa
│   ├── 00-contexto-handoff.md             # Este arquivo (passagem de bastão)
│   ├── 01-requisitos.md                   # Requisitos funcionais, não funcionais e regras
│   ├── 02-decisoes-arquitetura.md         # Decisões de stack, deploy único e SQL puro
│   ├── 03-regras-futuras.md               # Regras para fases pós-MVP
│   ├── 04-guia-execucao-e-ambiente.md     # Guia do XAMPP, DBeaver, .env e pipeline
│   ├── 05-modelagem-frontend.md           # Especificação detalhada da interface web
│   ├── 06-arquitetura-servidor-e-rotas.md # Lógica do main.py, rotas estáticas e centralização CSS
│   ├── kanban.md                          # Quadro Kanban oficial integrado ao Obsidian
│   └── ello_mineiro_postman_collection.json # Collection nativa pronta para o Postman
├── database/
│   └── seed.sql                           # Esquema MySQL com restrições e carga inicial
├── app/                                   # Backend FastAPI
│   ├── main.py                            # Ponto de entrada, rotas estáticas (/, /cadastro, /home, /recuperacao)
│   ├── db.py                              # Conexão PyMySQL pura parametrizada
│   ├── security.py                        # Argon2id e PyJWT
│   ├── security_guards.py                 # Validação de X-API-Key, mesma origem e Rate Limiting
│   ├── schemas.py                         # Validações com Pydantic v2
│   ├── dependencies.py                    # Leitura segura de cookie HttpOnly
│   ├── repositories/                      # usuarios.py e enderecos.py (SQL puro)
│   └── routers/                           # auth.py e me.py
├── frontend/                              # Interface web de produção
│   ├── index.html                         # Login (GET /)
│   ├── cadastro.html                      # Cadastro com ViaCEP (GET /cadastro)
│   ├── home.html                          # Dashboard do aluno (GET /home)
│   ├── recuperacao.html                   # Recuperação de senha (GET /recuperacao)
│   ├── static/                            # Arquivos estáticos servidos pelo backend
│   │   ├── css/style.css                  # Folha de estilos unificada e responsiva
│   │   ├── js/auth.js                     # Login, cadastro, ViaCEP, máscaras e CPF
│   │   ├── js/home.js                     # Route Guard e logout
│   │   └── img/                           # Logotipo institucional e fachada da escola
│   └── test/                              # Protótipos e referências visuais de rascunho
├── test_api.py                            # Bateria automatizada de testes locais (11 cenários)
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 6. Prompt para Iniciar a Próxima Sessão no Chat

> "Leia `docs/00-contexto-handoff.md`, `docs/06-arquitetura-servidor-e-rotas.md` e `docs/kanban.md`. O backend FastAPI com SQL puro, as validações de CPF e RG obrigatórios (NOT NULL) em todas as camadas, as proteções de segurança e o front-end web completo estão 100% implementados e homologados por 11 testes automatizados. Vamos iniciar a configuração do banco na nuvem (TiDB Cloud Serverless) e o deploy no Render."

