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
| Segurança de Mutabilidade | **Chave Privada (`X-API-Key`) + Mesma Origem (RNF18) + Rate Limiting (RNF07):** Mutações externas exigem `X-API-Key` (403 se ausente/inválida); navegação no site oficial opera com zero atrito via mesma origem; Rate Limiter barra abusos com 429 Too Many Requests |

---

## 3. Pontos de Atenção e Funcionalidades de Segurança

### 📌 3.1. Revisão da Obrigatoriedade de CPF e RG:
* **Contexto atual:** Atualmente no `seed.sql` e no `schemas.py`, os campos `cpf` e `rg` estão como opcionais (`NULL`), seguindo uma premissa inicial de LGPD.
* **Problema identificado pelo usuário:** Por ser um MVP de curso técnico de escopo fechado que provavelmente não terá uma fase posterior de secretaria escolar para preenchimento de documentos, manter CPF e RG opcionais fará com que eles fiquem permanentemente vazios/órfãos nos cadastros de teste.
* **Proposta para a próxima sessão:** Avaliar a alteração para torná-los **obrigatórios (`NOT NULL`)** no banco de dados, no schema Pydantic e no formulário do front-end.
* **Casos de exceção a definir:** Como tratar alunos estrangeiros ou imigrantes sem documentos nacionais (ex.: permitir validação de RNE/Passaporte no RG ou exigir apenas CPF com dígitos válidos).

### ✅ 3.2. Estratégia de Segurança das Rotas de Mutabilidade via Chave Privada (`.env` / Render) — [IMPLEMENTADO E VALIDADO 100%]:
* **Contexto e Objetivo:** Bloqueia requisições disparadas por scripts externos fora do site oficial (via cURL, Python, Postman ou outros domínios maliciosos que não possuam a chave de API), garantindo que apenas requisições legítimas do site do Ello Mineiro ou integrações autorizadas consigam disparar mutações (`/api/auth/register`, `/api/auth/login`, `/api/auth/logout`).
* **Implementação Realizada no Módulo [`app/security_guards.py`](app/security_guards.py):**
  1. **Armazenamento 100% Seguro e Privado:** Chave `API_KEY` cadastrada no arquivo `.env` (local) e prevista para variáveis de ambiente do Render (produção). Registrada como modelo em `.env.example`. Nunca exposta no JavaScript do cliente.
  2. **Validação para Integrações e Scripts Externos:** Chamadas externas que não tenham origem comprovada do site oficial precisam fornecer o cabeçalho `X-API-Key`. Se a chave for ausente ou incorreta, o backend rejeita com **`403 Forbidden`**. A Postman Collection oficial foi atualizada com a variável `{{api_key}}`.
  3. **Validação Transparente para o Front-end do Site (Zero Atrito para o Usuário):** Validação automática de mesma origem (RNF18) avaliando cabeçalhos nativos do navegador (`Sec-Fetch-Site: same-origin`, `Origin` e `Referer`). O usuário no navegador navega e preenche formulários sem precisar digitar nem conhecer a chave de API.
  4. **Proteções Complementares Integradas:**
     * **RNF18 (Validação de Origem):** Bloqueio estrito de disparos com `Origin` ou `Referer` externos ou de domínios cruzados não autorizados.
     * **RNF07 (Rate Limiting por IP):** Implementado via `RateLimiter` em memória (janela deslizante) aplicando limite de 10 tentativas/minuto para login e 5 cadastros/minuto para registro, retornando **`429 Too Many Requests`** com header explicativo `Retry-After`.
     * **Padrão de Geração CSPRNG:** Registrado em [docs/04-guia-execucao-e-ambiente.md](04-guia-execucao-e-ambiente.md) o padrão criptográfico seguro da indústria para geração da chave via terminal (`python -c "import secrets; print('ello_live_' + secrets.token_urlsafe(32))"`), desaconselhando terminantemente o uso de sites online.
     * **Matriz de Rotas:** Mapeamento explícito de quais rotas exigem `X-API-Key` documentado na seção 6.1 de [docs/01-requisitos.md](01-requisitos.md).
  5. **Bateria de Testes (`test_api.py`):** Expandida para **11 cenários automatizados** cobrindo bloqueio externo sem chave (403), chave errada (403), autorização com chave correta (201), cadastro com todos os opcionais preenchidos, cadastro com todos os campos opcionais nulos (`genero`, `cpf`, `rg`, `data_nasc`, `telefone`, `telefone_sec`), autorização transparente por mesma origem (201), integridade atômica com endereço (422), duplicidade (409), emissão de cookie HttpOnly e checagem de nulos no `/api/me`, logout e Rate Limiting (429). 100% aprovada.

---

## 4. Próxima Etapa de Execução (Passo 4 — Interface Web)

Com a API, o banco e a segurança de rotas 100% validados, a próxima atuação será focada na construção do front-end estático, seguindo rigorosamente a especificação do documento [docs/05-modelagem-frontend.md](05-modelagem-frontend.md):

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
│   ├── security_guards.py                 # Validação de X-API-Key, mesma origem e Rate Limiting
│   ├── schemas.py                         # Validações com Pydantic v2
│   ├── dependencies.py                    # Leitura segura de cookie HttpOnly
│   ├── repositories/                      # usuarios.py e enderecos.py (SQL puro)
│   └── routers/                           # auth.py e me.py
├── frontend/                              # Interface web
│   ├── index.html, cadastro.html, home.html # Telas finais de produção
│   ├── static/css, static/js              # Estilos e scripts oficiais
│   └── test/                              # Protótipos e referências visuais da equipe
├── test_api.py                            # Bateria automatizada de testes locais (11 cenários)
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 6. Prompt para Iniciar a Próxima Sessão no Chat

> "Leia `docs/00-contexto-handoff.md`, `docs/05-modelagem-frontend.md` e `docs/01-requisitos.md`. O backend FastAPI com SQL puro, o banco MySQL local e a segurança de rotas (X-API-Key, mesma origem e Rate Limiting) estão 100% implementados e validados por 11 testes automatizados. Vamos iniciar decidindo o ponto 3.1 do handoff (obrigatoriedade de CPF e RG) e, em seguida, construir a interface web do front-end adaptando os protótipos de `frontend/test/` conforme as especificações do documento 05."


