## 1. Projeto

- **O quê:** MVP do sistema de gestão da escola particular **Ello Mineiro**, trabalho em grupo da disciplina de **Banco de Dados** (curso técnico). Projeto de aprendizagem.
- **Escopo da Fase 1:** apenas **cadastro e login** de usuários, com senhas em hash (Argon2id), integridade atômica com endereço obrigatório e rotas de API servidas na mesma origem com cookie `HttpOnly`.
- **Estado atual:** **Backend FastAPI 100% implementado e validado** localmente contra o MySQL no XAMPP. Bateria de testes automatizados (`test_api.py`) passando com 100% de sucesso. Documentação técnica e OpenAPI totalmente sincronizados.
- **Idioma:** português (documentação, nomes de campos e commits).

## 2. Decisões já consolidadas

| Tema | Decisão |
|---|---|
| Banco | **MySQL** (esquema `database/seed.sql`). Desenvolvido e testado localmente no **XAMPP/DBeaver**; produção futura no **TiDB Cloud Serverless** |
| Backend | **Python + FastAPI**, arquitetura desacoplada em repositórios SQL puros (`PyMySQL`), segurança com **Argon2id** e JWT (`HS256`) |
| Front-end | HTML/CSS/JS estáticos **servidos pelo próprio backend** (`GET /` retorna `index.html`; API em `/api/*`). **Deploy único, mesma origem, sem CORS** |
| Sessão | Cookie **`HttpOnly; Secure; SameSite=Lax; Path=/`** (nome `access_token`). O navegador gerencia de forma transparente sem manipulação direta pelo JS |
| Integridade de Endereço | **Atomicidade total (RN04 / RNF19):** Todo cadastro exige obrigatoriamente um endereço completo. Não existem usuários sem endereço nem endereços órfãos |
| Perfil no cadastro | Todo usuário nasce com o perfil padrão **`Usuario`**. Perfis avançados (`Aluno`, `Professor`, etc.) existem no banco para o futuro |
| `user_login` | Nome de usuário escolhido pelo usuário (3–30 caracteres, `[a-zA-Z0-9._]`, case preservado no envio e exibição; busca e unicidade case-insensitive no MySQL `utf8mb4_unicode_ci`) |

---

## 3. Ponto de Atenção Prioritário para a Próxima Sessão

### 📌 Revisão da Obrigatoriedade de CPF e RG (Avaliar no início da próxima sessão):
* **Contexto atual:** Atualmente no `seed.sql` e no `schemas.py`, os campos `cpf` e `rg` estão como opcionais (`NULL`), seguindo uma premissa inicial de LGPD.
* **Problema identificado pelo usuário:** Por ser um MVP de curso técnico de escopo fechado que provavelmente não terá uma fase posterior de secretaria escolar para preenchimento de documentos, manter CPF e RG opcionais fará com que eles fiquem permanentemente vazios/órfãos nos cadastros de teste.
* **Proposta para a próxima sessão:** Avaliar a alteração para torná-los **obrigatórios (`NOT NULL`)** no banco de dados, no schema Pydantic e no formulário do front-end.
* **Casos de exceção a definir:** Como tratar alunos estrangeiros ou imigrantes sem documentos nacionais (ex.: permitir validação de RNE/Passaporte no RG ou exigir apenas CPF com dígitos válidos).

---

## 4. Próxima Etapa de Execução (Passo 4 — Interface Web)

Com a API e o banco 100% validados, a próxima atuação será focada na construção do front-end estático, seguindo rigorosamente a especificação do documento [docs/05-modelagem-frontend.md](05-modelagem-frontend.md):

1. **Estilos Globais (`frontend/static/css/style.css`):**
   * Design moderno e institucional para a *Escola Ello Mineiro* (CSS puro, responsivo, tipografia Inter, cards e feedbacks).
2. **Tela de Login (`frontend/index.html` — `GET /`):**
   * Formulário de login com identificador (`user_login` ou e-mail), senha e consumo de `POST /api/auth/login`.
3. **Tela de Cadastro (`frontend/cadastro.html` — `GET /cadastro`):**
   * Formulário com dados pessoais e endereço, máscaras inteligentes (telefone fixo 10 dígitos / celular 11 dígitos, CPF, CEP com envio limpo `\D`), Title Case inteligente para nomes, comboboxes (`genero`, `uf`), omissão de campos de sistema (`ativo`, `situacao`, `tipo`), validações em tempo real e autopreenchimento via **ViaCEP**.
4. **Tela Home / Dashboard (`frontend/home.html` — `GET /home`):**
   * Guarda de rota (redireciona para `/` se receber 401 de `GET /api/me`), visualização do perfil institucional, endereço cadastrado e botão de Logout.
   * *Adaptação dos Protótipos:* Utilizar os arquivos e imagens de referência em `frontend/test/` (rascunhos criados pela equipe) como guia visual para construir os layouts definitivos e semânticos.

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
│   ├── 05-modelagem-frontend.md           # Especificação completa do front-end
│   └── ello_mineiro_postman_collection.json # Collection nativa pronta para o Postman
├── database/
│   └── seed.sql                           # Esquema MySQL com restrições e carga inicial
├── app/                                   # Backend FastAPI
│   ├── main.py                            # App, rotas estáticas e /health
│   ├── db.py                              # Conexão PyMySQL pura parametrizada
│   ├── security.py                        # Argon2id e PyJWT
│   ├── schemas.py                         # Validações com Pydantic v2
│   ├── dependencies.py                    # Leitura segura de cookie HttpOnly
│   ├── repositories/                      # usuarios.py e enderecos.py (SQL puro)
│   └── routers/                           # auth.py e me.py
├── frontend/                              # Interface web
│   ├── index.html, cadastro.html, home.html # Telas finais de produção
│   ├── static/css, static/js              # Estilos e scripts oficiais
│   └── test/                              # Protótipos e referências visuais da equipe
├── test_api.py                            # Bateria automatizada de testes locais
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 6. Prompt para Iniciar a Próxima Sessão no Chat

> "Leia `docs/00-contexto-handoff.md`, `docs/05-modelagem-frontend.md` e `docs/01-requisitos.md`. O backend FastAPI com SQL puro e o banco MySQL local estão 100% implementados e testados com sucesso. Vamos iniciar avaliando o ponto prioritário da seção 3 do handoff (revisão da obrigatoriedade dos campos CPF e RG) e, em seguida, construir a interface web do front-end seguindo as especificações do documento 05."

