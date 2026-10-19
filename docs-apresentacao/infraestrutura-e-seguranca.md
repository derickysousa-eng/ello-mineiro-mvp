# Infraestrutura em Nuvem e Arquitetura de Segurança em Camadas

> **Finalidade:** Material técnico e roteiro de apresentação acadêmica do projeto **Escola Particular Ello Mineiro — MVP**.  
> **Tema:** Topologia de Infraestrutura (Render + TiDB Cloud Serverless) e Práticas de Segurança em Profundidade (*Defense in Depth*).

---

## 1. Visão Geral da Topologia de Nuvem

A arquitetura do projeto foi projetada no modelo **Monólito Modular de Mesma Origem (*Single-Origin*)**, com separação desacoplada entre a camada de aplicação/servidor web e a camada de banco de dados relacional distribuído.

```
                          ┌───────────────────────────────────────────────┐
                          │               CLIENTE / USUÁRIO               │
                          │     (Navegador Web Desktop ou Dispositivo)    │
                          └───────────────────────┬───────────────────────┘
                                                  │
                                                  │  HTTPS (TLS 1.3 / Porta 443)
                                                  │  (Comunicação Cifrada)
                                                  ▼
                          ┌───────────────────────────────────────────────┐
                          │                 PAAS: RENDER                  │
                          │           (Linux Container / Python 3)        │
                          │                                               │
                          │  • Servidor ASGI: Uvicorn na porta $PORT      │
                          │  • Framework: FastAPI (API REST + Front-end)  │
                          │  • Arquitetura Same-Origin (Zero CORS)        │
                          │  • Variáveis de Ambiente Injetadas na Memória │
                          └───────────────────────┬───────────────────────┘
                                                  │
                                                  │  MySQL sobre TLS/SSL (Porta 4000)
                                                  │  (Túnel Seguro Obrigatório DB_SSL=true)
                                                  ▼
                          ┌───────────────────────────────────────────────┐
                          │          DBAAS: TIDB CLOUD SERVERLESS         │
                          │          (AWS N. Virginia - us-east-1)        │
                          │                                               │
                          │  • Banco de Dados Relacional Distribuído      │
                          │  • 100% Compatível com protocolo MySQL        │
                          │  • Esquema Oficial: ello_mineiro              │
                          │  • Tabelas: Permissoes, Usuarios, Endereco    │
                          └───────────────────────────────────────────────┘
```

### Componentes da Infraestrutura:

| Camada | Provedor | Tecnologia / Serviço | Papel Arquitetural |
|---|---|---|---|
| **Aplicação Web (Full-Stack)** | **Render** | Web Service (Linux Container) | Executa o backend FastAPI e o servidor de arquivos estáticos (`/`, `/cadastro`, `/home`, `/recuperacao`, `/static`). |
| **Banco de Dados (DBaaS)** | **TiDB Cloud** | TiDB Serverless (AWS `us-east-1`) | Banco relacional distribuído NewSQL compatível com MySQL 8.0, escalável e de alta disponibilidade. |
| **Comunicação de Dados** | **Internet Pública Segura** | TLS 1.3 / SSL Nativo | Todo o tráfego externo e interno trafega sobre canais criptografados. |

> **Nota de Arquitetura Distribuída (AUTO_INCREMENT em Nuvem):** Por ser um banco NewSQL projetado para alta concorrência em múltiplos servidores, o TiDB Cloud aloca identificadores primários em lotes (`AUTO_ID_CACHE = 30000`) para cada sessão de conexão. Isso explica por que novos blocos de registros iniciam em `1`, `30001`, `60001` e `90001`, eliminando travas centrais de tabela sem quebrar a unicidade e a integridade referencial.

---

## 2. Padrão 12-Factor App: Zero Credenciais "Hardcoded" no Código

Uma das principais exigências de segurança corporativa e conformidade (LGPD, ISO 27001 e OWASP) é a **proibição estrita de credenciais, senhas ou segredos expostos diretamente no código-fonte (*hardcoded*)**.

No projeto Ello Mineiro, seguimos rigorosamente o terceiro princípio do manifesto **12-Factor App (Configurações no Ambiente)**:

```
    ┌──────────────────────┐         ┌────────────────────────┐
    │  Repositório Git     │         │  Ambiente Local / Dev  │
    │  (Código Público)    │         │  (.env não versionado) │
    ├──────────────────────┤         ├────────────────────────┤
    │ • Zero senhas        │         │ • python-dotenv        │
    │ • Zero chaves API    │         │ • Conexão Local / TiDB │
    │ • Apenas .env.example│         │ • .gitignore blindado  │
    └──────────────────────┘         └────────────────────────┘
                                                 ▲
                                                 │
                                     ┌───────────┴────────────┐
                                     │  Produção (Render)     │
                                     │  (Environment Secrets) │
                                     ├────────────────────────┤
                                     │ • Criptografado em repouso
                                     │ • Injeção direta no OS │
                                     │ • os.getenv("DB_PASS") │
                                     └────────────────────────┘
```

### Como a proteção opera na prática:

1. **Repositório Git 100% Limpo:**
   * O arquivo `.env` com senhas reais está incluído no `.gitignore` e **nunca sobe para o GitHub**.
   * O repositório armazena exclusivamente o arquivo [`.env.example`](file:///c:/Users/israe/Documents/ESTUDOS%20PROGRAMA%C3%87%C3%83O%20WEB/projeto-grau-tec/ello-mineiro-mvp/.env.example) com valores genéricos e descritivos.

2. **Isolamento no Painel do Render (Environment Secrets):**
   * As chaves de produção residem nos servidores do Render protegidas por criptografia de nível de infraestrutura.
   * Quando o contêiner inicia, o sistema operacional injeta essas variáveis diretamente na memória do processo (`os.environ`), sem gravar em nenhum arquivo de texto legível.

3. **Matriz de Variáveis de Ambiente do Sistema:**

| Variável | Finalidade Técnica | Exemplo de Valor (Produção) |
|---|---|---|
| `DB_HOST` | Endereço do cluster gerenciado | `gateway01.us-east-1.prod.aws.tidbcloud.com` |
| `DB_PORT` | Porta de rede do protocolo MySQL | `4000` |
| `DB_USER` | Usuário do banco com tenant ID | `2ijcpuBXGCD7u3f.root` |
| `DB_PASSWORD` | Senha de alta entropia gerada pelo TiDB | *(Segredo injetado no Render)* |
| `DB_NAME` | Nome do banco lógico da aplicação | `ello_mineiro` |
| `DB_SSL` | Ativação do túnel seguro TLS no PyMySQL | `true` |
| `JWT_SECRET_KEY` | Chave criptográfica para assinatura HMAC-SHA256 | *(Hash de 64 caracteres hexadecimais)* |
| `API_KEY` | Segredo para autorização de mutabilidade externa | *(Chave privada para integrações)* |
| `ENVIRONMENT` | Identificador do ciclo de vida | `production` |
| `COOKIE_SECURE` | Força a flag de transporte seguro no cookie | `true` |

---

## 3. Arquitetura de Segurança em Profundidade (*Defense in Depth*)

Adotamos a estratégia de **Defesa em Profundidade**, garantindo que se uma barreira de segurança falhar, múltiplas camadas adicionais continuem protegendo o sistema.

```
       [ Usuário / Atacante ]
                 │
                 ▼
     Camada 1: Transporte HTTPS / TLS
                 │
                 ▼
     Camada 2: Rate Limiting por IP (Anti-Brute Force / DoS)
                 │
                 ▼
     Camada 3: Guarda de Mutabilidade (X-API-Key + Same-Origin)
                 │
                 ▼
     Camada 4: Validação de Entrada (Pydantic v2 + Módulo 11)
                 │
                 ▼
     Camada 5: Autenticação Segura (Argon2id + Cookie HttpOnly)
                 │
                 ▼
     Camada 6: Banco de Dados Parametrizado (Anti-SQL Injection via PyMySQL)
```

---

### 3.1. Criptografia no Transporte de Dados (HTTPS e TLS para o Banco)

* **No Frontend:** Todo o tráfego entre o navegador do usuário e o Render é protegido por **HTTPS/TLS 1.3** com certificados SSL automatizados.
* **No Banco de Dados (`DB_SSL=true`):** O módulo [app/db.py](file:///c:/Users/israe/Documents/ESTUDOS%20PROGRAMA%C3%87%C3%83O%20WEB/projeto-grau-tec/ello-mineiro-mvp/app/db.py#L30-L34) configura o contexto criptográfico nativo:
  ```python
  if DB_SSL:
      ssl_context = ssl.create_default_context()
  ```
  Isso garante que todas as consultas SQL, senhas em trânsito e dados cadastrais trafeguem entre o Render (EUA) e o TiDB Cloud através de um **túnel TLS criptografado**, imune a ataques de interceptação de rede (*Man-in-the-Middle*).

---

### 3.2. A Guarda de Mutabilidade Segura: `X-API-Key` + *Same-Origin*

Implementamos em [app/security_guards.py](file:///c:/Users/israe/Documents/ESTUDOS%20PROGRAMA%C3%87%C3%83O%20WEB/projeto-grau-tec/ello-mineiro-mvp/app/security_guards.py) uma camada inteligente de proteção contra chamadas maliciosas de robôs ou clientes não autorizados:

* **O Problema Resolvido:** Se um atacante usar ferramentas como Postman, cURL ou robôs automatizados de spam para disparar cadastros em massa no endpoint `/api/auth/register`, como diferenciar esse tráfego do usuário legítimo usando o site?
* **A Solução:**
  1. **Navegador Oficial do Site (Mesma Origem):** Quando o usuário interage com o formulário em `/cadastro`, o navegador anexa automaticamente os cabeçalhos de segurança padronizados pelo W3C: `Sec-Fetch-Site: same-origin` e `Origin`. O backend reconhece que a requisição veio do próprio domínio e permite o processamento transparente com **zero atrito**.
  2. **Clientes Externos / Scripts:** Qualquer requisição externa que não provenha do navegador do site precisa obrigatoriamente apresentar o cabeçalho privado:
     ```http
     X-API-Key: sua_chave_privada_aqui
     ```
     Caso a chave esteja ausente ou errada, o servidor encerra a conexão instantaneamente com **`HTTP 403 Forbidden`**.

---

### 3.3. Autenticação e Sessões Blindadas contra Roubo (XSS e CSRF)

1. **Hash de Senha com Argon2id:**
   * Não utilizamos algoritmos obsoletos (MD5, SHA1) nem tradicionais sem resistência a hardware (SHA256 puro).
   * Utilizamos o **Argon2id**, vencedor oficial do *Password Hashing Competition*, parametrizado com salt aleatório e alto consumo computacional e de memória, tornando ataques de força bruta com placas de vídeo (GPUs/ASICs) inviáveis.
2. **Tokens JWT em Cookies `HttpOnly; Secure; SameSite=Lax`:**
   * **Por que não salvar no `localStorage`?** Se a aplicação tiver uma falha de XSS (*Cross-Site Scripting*), qualquer script malicioso consegue ler `localStorage.getItem("token")` e roubar a conta da vítima.
   * **Com Cookie `HttpOnly`:** O token fica inacessível ao JavaScript do navegador. Apenas o próprio browser inclui o cookie automaticamente nas requisições HTTP para a mesma origem, eliminando a principal vulnerabilidade de sessões web.
   * **Flag `Secure=true`:** O cookie só trafega através de conexões HTTPS criptografadas.
   * **Flag `SameSite=Lax`:** Bloqueia requisições forjadas vindas de links externos (proteção nativa contra CSRF).

---

### 3.4. Rate Limiting por IP (Proteção contra Brute Force - RNF07)

* O backend conta com um algoritmo em memória de **Janela Deslizante (*Sliding Window Rate Limiter*)** implementado em [app/security_guards.py](file:///c:/Users/israe/Documents/ESTUDOS%20PROGRAMA%C3%87%C3%83O%20WEB/projeto-grau-tec/ello-mineiro-mvp/app/security_guards.py).
* Se um determinado endereço IP tentar adivinhar senhas no `/api/auth/login` mais de 10 vezes consecutivas ou disparar cadastros em massa no `/api/auth/register`, o servidor bloqueia o IP temporariamente:
  * Responde com código **`HTTP 429 Too Many Requests`**.
  * Retorna o cabeçalho padronizado **`Retry-After: <segundos>`** informando o tempo exato de espera obrigatório antes da próxima tentativa.

---

### 3.5. Defesa em Duas Camadas na Validação de Dados

* **Camada do Cliente (Front-end):**
  * Máscaras dinâmicas e validação interativa imediata no arquivo [auth.js](file:///c:/Users/israe/Documents/ESTUDOS%20PROGRAMA%C3%87%C3%83O%20WEB/projeto-grau-tec/ello-mineiro-mvp/frontend/static/js/auth.js).
  * Algoritmo de Módulo 11 de CPF em tempo real, validação de formato de e-mail e medidor de força de senha.
* **Camada do Servidor (Backend):**
  * Esquemas rigorosos do **Pydantic v2** em [schemas.py](file:///c:/Users/israe/Documents/ESTUDOS%20PROGRAMA%C3%87%C3%83O%20WEB/projeto-grau-tec/ello-mineiro-mvp/app/schemas.py). Mesmo que um atacante burle o JavaScript ou envie um payload direto via API, os cálculos matemáticos do CPF, RG e sanitização de dados são recalculados no servidor.
  * O manipulador de exceções em [main.py](file:///c:/Users/israe/Documents/ESTUDOS%20PROGRAMA%C3%87%C3%83O%20WEB/projeto-grau-tec/ello-mineiro-mvp/app/main.py) traduz eventuais rejeições para mensagens amigáveis em língua portuguesa.

---

## 4. Roteiro Sugerido para Apresentação em Grupo (Pitch Técnico)

Ao apresentar a infraestrutura e a segurança para a banca e professores, estruturem a explicação em 4 etapas diretas:

### 1. A Escolha da Infraestrutura (Nuvem de Alta Performance)
> *"Para colocar o projeto no ar com padrão de produção real, integramos dois serviços de ponta em nuvem: o **Render** para a hospedagem do backend FastAPI e páginas estáticas em arquitetura de mesma origem, e o **TiDB Cloud Serverless** na AWS para o banco de dados relacional distribuído. Essa combinação nos garantiu alta disponibilidade, latência mínima e custo zero."*

### 2. A Política de Segurança 12-Factor App (Zero Segredos no Código)
> *"Um diferencial crítico do nosso projeto é que nenhuma senha, chave de API ou credencial de banco de dados existe 'chumbada' no código-fonte. Seguindo o padrão corporativo 12-Factor App, o repositório Git contém apenas um arquivo de exemplo `.env.example`, enquanto no servidor Render todas as variáveis são injetadas de forma criptografada diretamente na memória do processo em tempo de execução."*

### 3. O Modelo de Defesa em Profundidade (*Defense in Depth*)
> *"A segurança não depende de uma única trava. Nós implementamos múltiplas camadas: criptografia de ponta a ponta com HTTPS e TLS no banco; proteção de mutabilidade com `X-API-Key` contra robôs externos; proteção contra roubo de contas armazenando tokens JWT em cookies protegidos com a flag `HttpOnly`; e um limitador de requisições por IP contra ataques de força bruta que devolve o código HTTP 429."*

### 4. Demonstração e Fechamento
> *"Com isso, o sistema está hoje 100% no ar, homologado por uma bateria de 11 testes automatizados de segurança e integridade referencial, e pronto para receber novos alunos com total confiabilidade técnica."*
