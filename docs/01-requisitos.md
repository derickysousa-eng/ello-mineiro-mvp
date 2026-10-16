# Requisitos — MVP Ello Mineiro (Fase 1: Cadastro e Login)

> Status: **rascunho para revisão**. Nenhuma implementação foi iniciada.
>
> Regras de negócio válidas para o futuro, mas **fora do código desta fase**, estão em [03-regras-futuras.md](03-regras-futuras.md).

## 1. Escopo

**Dentro (Fase 1):** cadastro público de usuários (sempre com o perfil padrão `Usuario`), login, tela Home pós-login, armazenamento seguro de senhas.

**Fora (fases futuras):** promoção de perfil pelo setor administrativo, matrícula do aluno e registro de funcionário, vínculo com turmas, notas, presença, matérias, calendário acadêmico, consulta de professores. Ver [03-regras-futuras.md](03-regras-futuras.md). Os perfis `Aluno`, `Professor`, `Suporte` e `Administrativo` já existem no banco, mas **não são atribuídos por nenhuma tela ou rota do MVP**.

## 2. Atores

| Ator | Descrição |
|---|---|
| Visitante | Não autenticado; pode se cadastrar e fazer login |
| Usuário | Autenticado com o perfil padrão `Usuario` (único ator logado no MVP) |
| Aluno, Professor, Suporte, Administrativo | Perfis existentes no banco; atribuídos apenas em fases futuras (ver doc 03) |

## 3. Requisitos Funcionais (RF)

| ID | Requisito | Prioridade |
|---|---|---|
| RF01 | O sistema deve permitir cadastrar um usuário com: nome, e-mail, `user_login` (nome de usuário escolhido por ele), senha, endereço obrigatório e dados pessoais opcionais (CPF, RG, nascimento, gênero, telefones). **O formulário não oferece escolha de perfil** | Alta |
| RF02 | O sistema deve exigir obrigatoriamente o cadastro de ao menos um endereço residencial/comercial no momento do registro. Cadastros sem endereço ou com dados de logradouro incompletos são rejeitados com erro 422 | Alta |
| RF03 | O sistema deve validar unicidade de `user_login`, `email`, `cpf` e `rg` e retornar erro claro em caso de duplicidade | Alta |
| RF04 | O sistema deve validar formato de e-mail, CPF (dígitos verificadores), CEP, UF e telefone (exatamente 11 dígitos numéricos: DDD + celular; o front envia só dígitos, sem máscara) | Alta |
| RF05 | O usuário deve poder fazer login com `user_login` **ou** `email` + senha | Alta |
| RF06 | Em login válido, a API deve emitir um token de acesso (JWT) com expiração, entregue **somente** em cookie `HttpOnly` via `Set-Cookie` (o token **não** aparece no corpo da resposta) | Alta |
| RF07 | Em login inválido, a API deve responder com mensagem genérica (sem revelar se o usuário existe) | Alta |
| RF08 | Usuários com `ativo = false` não podem fazer login | Alta |
| RF09 | Os dados da Home só podem ser obtidos com cookie de sessão válido; se `GET /api/me` responder `401`, o front redireciona para o login (`/`) | Alta |
| RF10 | A API deve expor uma rota autenticada que retorna os dados do usuário logado (`GET /me`), sem a senha | Alta |
| RF11 | O perfil (`permissao_nome`) deve ser lido do banco (nunca do corpo da requisição) e respeitado nas rotas protegidas; no MVP, todo usuário tem o perfil `Usuario` | Média |
| RF13 | Todo novo cadastro deve receber automaticamente o perfil `Usuario`; qualquer campo de perfil enviado na requisição deve ser ignorado ou rejeitado | Alta |
| RF12 | O usuário deve poder encerrar a sessão por `POST /api/auth/logout`, que apaga o cookie do token (`Max-Age=0`) | Média |

### Decisão de negócio (resolvida)
O README antigo previa que a tela de cadastro permitisse escolher o perfil, o que deixaria qualquer visitante se cadastrar como `Administrativo`. **Decisão:** o cadastro público **não** pede perfil. Todo usuário nasce com o perfil padrão `Usuario` (acesso básico: calendário e dados públicos, sem dados pessoais de terceiros, em linha com a LGPD). Os demais perfis serão liberados futuramente pelo setor administrativo (ver [03-regras-futuras.md](03-regras-futuras.md)). O primeiro administrador, quando necessário, será criado por seed/script, nunca por tela.

### Identificador de login (resolvido)
O `user_login` é um **nome de usuário escolhido pelo próprio usuário** no cadastro (3 a 30 caracteres, apenas `a-z`, `0-9`, `.`, `_`; único; guardado em minúsculas). Ele **não é** a matrícula nem o registro funcional. Estes são identificadores institucionais, emitidos pela escola no futuro, em tabelas próprias.

### Armazenamento do JWT (resolvido)
O JWT fica em **cookie `HttpOnly; Secure; SameSite=Lax; Path=/`**, definido pelo backend no login. O JavaScript do front **não lê nem guarda** o token: o navegador o envia sozinho em toda chamada a `/api/*` (mesma origem). Motivos: resistência a roubo do token por XSS e encaixe natural com a arquitetura de mesma origem. Detalhes em [02-decisoes-arquitetura.md](02-decisoes-arquitetura.md#5-estratégia-de-autenticação).

## 4. Requisitos Não Funcionais (RNF)

### Segurança
| ID | Requisito |
|---|---|
| RNF01 | Senhas armazenadas apenas como hash com **Argon2id** ou **bcrypt** (salt automático). Nunca em texto puro nem em logs |
| RNF02 | Política de senha: mínimo 8 caracteres (recomendado 10+), validada no backend |
| RNF03 | Toda comunicação via **HTTPS** |
| RNF04 | SQL puro com queries **sempre parametrizadas** (`%s`), concentrado em `app/repositories/` (prevenção de SQL Injection). Ver [02-decisoes-arquitetura.md](02-decisoes-arquitetura.md) |
| RNF05 | Front e API na mesma origem (sem CORS habilitado). Cookie do token com `HttpOnly; Secure; SameSite=Lax; Path=/` e `Max-Age` igual à expiração do JWT |
| RNF06 | Segredos (chave JWT, string de conexão, API_KEY) em variáveis de ambiente (.env / Render), nunca no Git |
| RNF07 | **Rate Limiting por IP (Sliding Window em memória):** Máx 10 tentativas/min no login e 5 cadastros/min no registro, mitigando força bruta e spam (retorna HTTP 429 Too Many Requests com header `Retry-After`) |
| RNF08 | JWT com expiração curta (ex.: 30–60 min) e algoritmo fixo (HS256) |
| RNF09 | Dados pessoais (CPF, RG) tratados conforme **LGPD**: coletar só o necessário, nunca expor em respostas desnecessárias |
| RNF10 | Mensagens de erro não vazam detalhes internos (stack trace, SQL) |
| RNF18 | **Proteção de Rotas de Mutabilidade e CSRF:** Chamadas externas exigem `X-API-Key` (rejeição 403 Forbidden se ausente/inválida); chamadas do site oficial operam com zero atrito via validação de mesma origem (`Sec-Fetch-Site: same-origin`, `Origin` e `Referer`). Bloqueio estrito de origens cruzadas |
| RNF19 | **Atomicidade e Integridade Transacional Usuário-Endereço:** O sistema garante que não existam endereços órfãos (assegurado por `usuario_id INT NOT NULL` e `FOREIGN KEY ... ON DELETE CASCADE`) nem usuários sem endereço (assegurado por validação obrigatória no schema de entrada e transação atômica no backend com `commit`/`rollback` conjunto) |

### Qualidade
| ID | Requisito |
|---|---|
| RNF11 | API REST em JSON, com códigos HTTP corretos (201, 400, 401, 403, 409, 422, 429) |
| RNF12 | Documentação automática da API (OpenAPI/Swagger — nativa do FastAPI) |
| RNF13 | Custo de hospedagem **zero** |
| RNF14 | Banco normalizado (mínimo 3FN) com scripts versionados no repositório |
| RNF15 | Código e documentação em português (nomes de campos já seguem isso) |
| RNF16 | Tempo de resposta aceitável (< 1s em operação normal; cold start do plano grátis é tolerado) |
| RNF17 | Responsividade básica do front (mobile e desktop) |

## 5. Regras de Negócio

- RN01: `user_login` (nome de usuário) é único e imutável após criado. Não representa matrícula nem registro funcional.
- RN02: Todo usuário tem exatamente 1 perfil. No cadastro, o perfil é sempre `Usuario`.
- RN05: O perfil nunca é definido pelo próprio usuário nem pelo corpo da requisição de cadastro.
- RN03: Exclusão de usuário é **lógica** (`ativo = false`), preservando histórico futuro (notas, presença).
- RN04: Todo usuário tem obrigatoriamente ao menos 1 endereço cadastrado no momento do registro. Um usuário pode ter vários endereços, mas apenas um ativo por tipo. Endereços órfãos e usuários sem endereço são impossíveis no sistema.

## 6. Rotas da API e Matriz de Segurança

### 6.1. Matriz Completa de Proteção das Rotas (X-API-Key vs Mesma Origem vs Cookie)

Abaixo está o mapeamento explícito de todas as rotas da aplicação, detalhando quais exigem o cabeçalho `X-API-Key`, quais aceitam navegação transparente do front-end oficial, quais exigem cookie de sessão e quais possuem rate limiting:

| Rota | Método | Exige `X-API-Key`? | Front-end Oficial (Mesma Origem)? | Exige Cookie `access_token`? | Rate Limit por IP (RNF07)? | Tipo / Justificativa de Segurança |
|---|---|:---:|:---:|:---:|:---:|---|
| `/api/auth/register` | `POST` | **SIM** (para scripts externos) | **SIM** (zero atrito, via `Sec-Fetch-Site` / `Origin`) | NÃO | **SIM** (máx 5 req/min) | **Mutabilidade pública.** Bloqueia scripts/bots externos e criação massiva de contas. |
| `/api/auth/login` | `POST` | **SIM** (para scripts externos) | **SIM** (zero atrito, via `Sec-Fetch-Site` / `Origin`) | NÃO | **SIM** (máx 10 req/min) | **Mutabilidade pública.** Bloqueia scanners, força bruta e ataques de dicionário. |
| `/api/auth/logout` | `POST` | **SIM** (para scripts externos) | **SIM** (zero atrito, via `Sec-Fetch-Site` / `Origin`) | **SIM** (revoga cookie) | NÃO | **Mutabilidade de sessão.** Proteção contra CSRF e revogação arbitrária de sessões. |
| `/api/me` | `GET` | **NÃO** | **SIM** | **SIM** (`HttpOnly; Secure`) | NÃO | **Leitura autenticada.** A segurança é assegurada exclusivamente pelo JWT no cookie. |
| `/health` | `GET` | **NÃO** | **SIM** | NÃO | NÃO | **Monitoramento público.** Endpoint leve para health check do Render, uptime e ping. |
| `/` | `GET` | **NÃO** | **SIM** | NÃO | NÃO | **Página pública.** Entrega do HTML da tela de Login (`index.html`). |
| `/cadastro` | `GET` | **NÃO** | **SIM** | NÃO | NÃO | **Página pública.** Entrega do HTML do formulário de Cadastro (`cadastro.html`). |
| `/home` | `GET` | **NÃO** | **SIM** | NÃO (dados protegidos via `/api/me`) | NÃO | **Página de dashboard.** Entrega do HTML (`home.html`); o JS redireciona se `/api/me` for 401. |
| `/static/*` | `GET` | **NÃO** | **SIM** | NÃO | NÃO | **Arquivos estáticos públicos.** Servimento de CSS, JS e imagens institucionais. |

> **Regra Fundamental de `X-API-Key`:** O cabeçalho `X-API-Key` é obrigatório **apenas para rotas de mutabilidade (`POST`) quando disparadas por clientes externos (Postman, scripts Python/cURL, integrações externas)**. O front-end oficial servido na mesma origem opera com **zero atrito**, sendo autorizado automaticamente pelo backend através da validação dos cabeçalhos legítimos de navegador (`Sec-Fetch-Site: same-origin`, `Origin` e `Referer`). Rotas de leitura (`GET /api/me`, `GET /health` e páginas estáticas) **nunca** exigem `X-API-Key`.


Exemplo de login:
```http
POST /api/auth/login
Content-Type: application/json

{ "identificador": "maria.silva ou maria@email.com", "senha": "********" }
```
```http
HTTP/1.1 200 OK
Set-Cookie: access_token=<jwt>; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=3600
Content-Type: application/json

{ "mensagem": "Login realizado com sucesso", "expires_in": 3600 }
```

Exemplo de logout:
```http
POST /api/auth/logout
```
```http
HTTP/1.1 204 No Content
Set-Cookie: access_token=; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=0
```

> O token **nunca** vai no corpo da resposta. Em login inválido: `401` com mensagem genérica (RF07). Em rota protegida sem cookie ou com token expirado: `401`.

## 7. Revisão do `database/seed.sql`

| Ponto | Situação |
|---|---|
| `senha VARCHAR(255)` | **Feito:** renomeada para `senha_hash` (255 comporta bcrypt ~60 e Argon2id ~100) |
| Perfil padrão | **Feito:** `Usuario` inserido em `Permissoes` e `permissao_nome DEFAULT 'Usuario'` |
| Comentário de `user_login` | **Feito:** "nome de usuário escolhido pelo usuário" |
| `Permissoes` com PK textual | Mantida (ok para MVP; `ON UPDATE CASCADE` já mitiga) |
| `cpf`, `rg` UNIQUE e nullable | Mantidos opcionais (LGPD, doc 03 §6). MySQL permite vários NULL |
| `telefone VARCHAR(11)` | **Decidido:** só dígitos, DDD + número (11). Aplicado em `telefone` e `telefone_sec` |
| `atualizado_em` / `ultimo_login` | **Decidido:** fora do MVP (previstos como auditoria futura, doc 03 §7) |
| `Endereco.situacao` | **Feito:** `NOT NULL DEFAULT 'ATIVO'` + `CHECK (situacao IN ('ATIVO','INATIVO'))`. O backend também valida (o `CHECK` só é aplicado no MySQL 8.0.16+; no TiDB depende de `tidb_enable_check_constraint`) |
| Índices | `user_login` e `email` já têm índice via UNIQUE |
| Charset | **Feito:** tabelas com `utf8mb4` / `utf8mb4_unicode_ci` |
| Local do arquivo | **Feito:** movido da raiz para `database/seed.sql` |
| README | **Feito:** introduções unificadas e stack alinhada |

## 8. Próximos passos
1. Revisar e aprovar este documento.
2. ~~Fechar decisões em [02-decisoes-arquitetura.md](02-decisoes-arquitetura.md)~~ (resta só o plano B do banco).
3. ~~Ajustar `seed.sql`~~ (itens opcionais em aberto na seção 7).
4. ~~Atualizar o `README.md`~~.
5. Iniciar o backend.
