# Modelagem e Especificação da Interface Web (Front-end) — Ello Mineiro MVP

> Este documento detalha a arquitetura, telas, contratos de integração, comportamento de validação e experiência do usuário (UX) do front-end estático da aplicação, servido na mesma origem pelo FastAPI.

---

## 1. Princípios Arquiteturais do Front-end

1. **Mesma Origem (Zero CORS):**
   * O front-end é servido diretamente pelo FastAPI através das rotas de página (`GET /`, `GET /cadastro`, `GET /home`) e montagem estática (`/static`).
   * Todas as requisições à API utilizam URLs relativas (`/api/auth/...`, `/api/me`), eliminando configurações de domínio cruzado.
2. **Pilha Tecnológica Pura (Vanilla):**
   * **Estrutura:** HTML5 semântico com acessibilidade básica.
   * **Estilo:** CSS3 moderno utilizando variáveis CSS (Design Tokens), Flexbox e CSS Grid. Responsividade total para smartphones, tablets e desktops sem dependência de frameworks externos (sem Tailwind ou Bootstrap).
   * **Lógica:** JavaScript puro (ES6+) consumindo a API via `Fetch API` nativa.
3. **Gerenciamento Transparente de Sessão (Cookie HttpOnly):**
   * Como o token JWT trafega no cookie `access_token` configurado com `HttpOnly`, o JavaScript **não manipula tokens manualmente** nem adiciona cabeçalhos `Authorization: Bearer`.
   * O próprio navegador anexa e envia o cookie automaticamente em todas as requisições para a mesma origem.
4. **Resiliência e Feedback Visual:**
   * Estados de carregamento (*loading spinners* ou botões desabilitados) durante o envio.
   * Mensagens de erro claras e amigáveis para códigos HTTP retornados pelo backend (`401`, `409`, `422`, `429`, `500`).
5. **Segurança de Mutabilidade Transparente (Sem Exposição de Chaves):**
   * Como o front-end é servido pelo FastAPI na mesma origem, o navegador anexa automaticamente os cabeçalhos de contexto de origem (`Sec-Fetch-Site: same-origin`, `Origin`), permitindo mutações transparentes sem necessidade de expor chaves de API (`API_KEY`) no código JavaScript do cliente. Clientes externos (Postman/scripts) utilizam o cabeçalho `X-API-Key`.

---

## 2. Mapa de Telas e Especificação

### 2.1. Tela de Login (`frontend/index.html` — Rota `GET /`)
* **Objetivo:** Ponto de entrada do sistema para autenticação de usuários cadastrados.
* **Componentes da Interface:**
  * Card centralizado com identidade visual da *Escola Particular Ello Mineiro*.
  * Campo **Identificador**: `input type="text"`, com suporte a preenchimento tanto do nome de usuário (`user_login`) quanto do e-mail cadastrado (conforme requisito **RF05**).
  * Campo **Senha**: `input type="password"`, com botão de alternar visualização (olho ocultar/mostrar senha).
  * Botão de submissão **"Entrar"**.
  * Link para recuperação de senha: *"Esqueci minha senha"* (no MVP exibe aviso informativo, ver seção 4).
  * Botão/Link para novo cadastro: *"Ainda não tem conta? Cadastre-se aqui"*.
* **Comportamento e Integração:**
  * Dispara `POST /api/auth/login` com payload:
    ```json
    { "identificador": "...", "senha": "..." }
    ```
  * Se `200 OK`: O navegador recebe o cookie `access_token` via `Set-Cookie`. O JavaScript exibe feedback de sucesso e redireciona imediatamente para `/home`.
  * Se `401 Unauthorized`: Exibe alerta visual amigável: *"Identificador ou senha incorretos."*
  * Se `422`: Alerta de dados inválidos.

---

### 2.2. Tela de Cadastro (`frontend/cadastro.html` — Rota `GET /cadastro`)
* **Objetivo:** Registro de novos usuários com o perfil padrão institucional `Usuario` e endereço residencial obrigatório.
* **Campos do Formulário:**
  1. **Credenciais de Acesso:**
     * `Nome de Usuário` (`user_login`): campo de texto (3 a 30 caracteres alfanuméricos, ponto ou sublinhado). **Encaminhado exatamente como o usuário digitou** (ver seção 3.3).
     * `E-mail` (`email`): campo de e-mail com validação estrutural em tempo real.
     * `Senha` (`senha`): campo de senha com indicador visual de requisitos (mínimo 8 caracteres) e barra de força.
  2. **Dados Pessoais:**
     * `Nome Completo` (`nome`): campo de texto obrigatório, formatado e enviado em **Title Case** inteligente (ver seção 3.2).
     * `Gênero` (`genero`): **Combobox (`<select>`)** padronizado com diretrizes do IBGE (ver seção 3.4).
     * `Data de Nascimento` (`data_nasc`): seletor de data (`type="date"`).
     * `CPF` (`cpf`): campo com máscara dinâmica `000.000.000-00`, validação de 11 dígitos e cálculo matemático dos dígitos verificadores (módulo 11) em tempo real.
     * `RG` (`rg`): campo alfanumérico flexível (de 7 a 14 caracteres alfanuméricos e pontuação), compatível com os diferentes formatos de RG estaduais (ex.: MG, SP) e com a coluna `VARCHAR(30)` do banco.
     * `Telefone Principal` (`telefone`): campo com máscara inteligente adaptativa para **fixo (10 dígitos)** ou **celular (11 dígitos)**.
     * `Telefone Secundário` (`telefone_sec`): opcional com a mesma máscara inteligente.
  3. **Endereço Residencial (Obrigatório — RN04 / RNF19):**
     * `CEP` (`cep`): campo com máscara `00000-000`. Ao completar 8 dígitos, consulta a API **ViaCEP** e autopreencha logradouro, bairro, cidade e UF.
     * `Logradouro / Rua` (`rua`): preenchido via CEP e ajustável manualmente caso necessário.
     * `Número` (`numero`): obrigatório.
     * `Complemento` (`complemento`): opcional (ex: Apto 201, Bloco B).
     * `Bairro` (`bairro`): autopreenchido via CEP e ajustável manualmente.
     * `Cidade` (`cidade`): preenchido automaticamente via CEP, liberando edição manual caso o serviço externo esteja indisponível (ver seção 3.4).
     * `UF` (`uf`): **Combobox (`<select>`)** com as 27 Unidades Federativas do Brasil (ver seção 3.4).

---

## 3. Especificações Detalhadas de Regras e Comportamento dos Campos

### 3.1. Máscaras Dinâmicas e Higienização de Dados para Envio
* **Telefones (Fixo vs Celular):**
  * O formulário aplica formatação adaptativa em tempo real:
    * Se tiver até 10 dígitos: formata no padrão fixo: `(XX) XXXX-XXXX` (ex: `(31) 3222-0000`).
    * Ao digitar o 11º dígito: reformata automaticamente para padrão celular: `(XX) 9XXXX-XXXX` (ex: `(31) 99659-4444`).
  * **Higienização para Envio:** No momento de montar o payload JSON para envio à API/Banco, todos os caracteres não numéricos são removidos (`telefone.replace(/\D/g, "")`). O backend recebe apenas dígitos puros (`"3132220000"` ou `"31996594444"`).
* **CPF e CEP:**
  * O CPF é exibido como `000.000.000-00`, mas enviado limpo com 11 dígitos (`"12345678901"`).
  * O CEP é exibido como `00000-000`, mas enviado limpo com 8 dígitos (`"30110000"`).

### 3.2. Capitalização de Nome Próprio (Title Case) e Tratativa de Complicações
* **Regra de Negócio:**
  * A primeira letra de cada nome próprio deve ser maiúscula (Title Case), tanto na interface quanto no armazenamento no banco de dados.
* **Análise de Complicações e Solução Adotada:**
  1. *Preposições da língua portuguesa:* Nomes brasileiros contêm preposições e conjunções que não devem ser capitalizadas quando no meio do nome (ex: "Carlos da Silva", "Maria das Dores e Santos", e **não** "Carlos Da Silva" ou "Maria Das Dores E Santos").
  2. *UX durante a digitação:* Forçar a capitalização no evento `input` enquanto o usuário digita pode gerar travamento de cursor e impedir que o usuário insira minúsculas conscientemente.
  3. *Tratativa:*
     * A formatação em Title Case no front-end é disparada no evento `blur` (quando o usuário sai do campo) e no momento do `submit`.
     * O algoritmo preserva em minúsculas as preposições conhecidas: `de`, `da`, `do`, `das`, `dos`, `e` (exceto se for a primeira palavra do nome).
     * **Validação Dupla no Backend:** O schema Pydantic (`formatar_nome_proprio` em `app/schemas.py`) também aplica essa mesma higienização antes de persistir no MySQL, garantindo consistência mesmo se a API for chamada externamente.

### 3.3. Preservação do `user_login` e Análise de Case Sensitivity
* **Envio Preservado:**
  * O campo `user_login` é enviado exatamente da forma como o usuário digitou (ex: se digitou `Carlos.Silva`, é enviado `Carlos.Silva`, sem conversão forçada para minúsculas).
* **Análise Técnica no MySQL (`utf8mb4_unicode_ci`):**
  * O banco de dados utiliza a collation com sufixo `_ci` (*Case-Insensitive*).
  * **Comportamento de Unicidade (`UNIQUE`):** O MySQL impede colisões de login independentemente de caixa alta ou baixa. Ou seja, se existir `Carlos.Silva`, nenhum outro usuário conseguirá cadastrar `carlos.silva` ou `CARLOS.SILVA`.
  * **Comportamento de Autenticação (Login):** Na consulta `WHERE user_login = %s`, o MySQL localiza o usuário mesmo se ele digitar em maiúsculas ou minúsculas na tela de login.
  * **Comportamento de Armazenamento:** O MySQL armazena o valor com o *casing* exato em que foi inserido, permitindo que a interface do usuário exiba `@Carlos.Silva` exatamente como o usuário escolheu.

### 3.4. Componentes Combobox (`<select>`) vs Inputs de Texto
* **Gênero (`genero`):**
  * Implementado como `<select>` com opções inclusivas alinhadas às diretrizes do IBGE: `Feminino`, `Masculino`, `Outro`, `Prefiro não informar`. No HTML, a opção *"Prefiro não informar"* envia valor compatível com a coluna `genero VARCHAR(20)` do banco de dados (ex: `value="Não informado"`).
* **Unidade Federativa (`uf`):**
  * Implementado como `<select>` com as 27 siglas de estados brasileiros (AC, AL, AP, AM, BA, CE, DF, ES, GO, MA, MT, MS, MG, PA, PB, PR, PE, PI, RJ, RN, RS, RO, RR, SC, SP, SE, TO). Isso elimina erros de digitação e siglas inválidas.
* **Cidade (`cidade`) — Autopreenchimento e Contingência:**
  * O Brasil possui mais de 5.570 municípios. Carregar um combobox estático com todos os municípios deixaria a página com mais de 500 KB desnecessários de HTML.
  * **Solução:** O campo `cidade` é autopreenchido via **ViaCEP** a partir do CEP digitado. Permanece bloqueado por padrão para precisão, mas é liberado automaticamente para edição manual caso o serviço externo falhe (offline/timeout) ou retorne CEP genérico/rural.

### 3.5. Campos Omitidos da Interface (Regras de Negócio e Valores Default)
Os seguintes campos **não possuem e não devem possuir campos de preenchimento no front-end**, sendo determinados estritamente pelo backend e regras de banco de dados:
1. `ativo` (tabela `Usuarios`): Todo usuário registrado no fluxo público nasce ativo (`ativo = TRUE` / `1`). O usuário não escolhe seu status de ativação.
2. `situacao` (tabela `Endereco`): Todo endereço recém-cadastrado é ativado imediatamente (`situacao = 'ATIVO'`).
3. `tipo` (tabela `Endereco`): No MVP escolar, o endereço solicitado no cadastro de alunos/usuários é exclusivamente residencial. O valor padrão `"Residencial"` é atribuído automaticamente pelo schema do backend (`EnderecoCreateSchema`) e pela restrição `DEFAULT 'Residencial'` da tabela.

### 3.6. Validação Interativa em Tempo Real
O formulário de cadastro fornece feedback imediato ao usuário nos eventos `input` e `blur`, antes do envio:
* **E-mail:** Validação estrutural de formato (`usuario@dominio.com`) com mensagem de erro visual se o formato for inválido.
* **CPF:** Além da máscara visual de 11 dígitos, executa em tempo real o algoritmo oficial dos dígitos verificadores (módulo 11) e rejeita sequências repetidas (`111.111.111-11`), alertando instantaneamente se o número for inválido.
* **RG:** Validação de formato alfanumérico e comprimento válido (7 a 14 caracteres).
* **Senha:** Indicador visual de complexidade (mínimo 8 caracteres, barra de progresso verde/vermelha).
* **Bloqueio de Submissão:** O botão de cadastro permanece desabilitado ou impede o envio com destaque visual em vermelho caso algum campo obrigatório possua erro ativo.

---

## 4. Estrutura de Arquivos Estáticos e Mapeamento de Protótipos

A estrutura de arquivos do front-end divide-se entre as **páginas oficiais de produção** (servidas pelo FastAPI) e os **protótipos de referência** da equipe:

```
frontend/
├── index.html               # Tela de Login final de produção (servida em "GET /")
├── cadastro.html            # Tela de Cadastro final de produção (servida em "GET /cadastro")
├── home.html                # Dashboard autenticado final (servido em "GET /home")
├── static/
│   ├── css/
│   │   └── style.css        # Folha de estilos institucional unificada e responsiva
│   ├── js/
│   │   ├── auth.js          # Lógica de login, cadastro, máscaras, validações e ViaCEP
│   │   └── home.js          # Guarda de rota do dashboard e logout
│   └── img/                 # Logotipos e imagens institucionais otimizadas
└── test/                    # Protótipos e referências visuais da equipe
    ├── login.html           # Protótipo da tela de login -> base para frontend/index.html
    ├── cadastro.html        # Protótipo do cadastro -> base para frontend/cadastro.html
    ├── index.html           # Protótipo do painel acadêmico -> base para frontend/home.html
    ├── recuperacao.html     # Protótipo da recuperação de senha (demonstrativo pós-MVP)
    ├── logo.png             # Logo preliminar da Escola Ello Mineiro
    └── escola.png           # Imagem ilustrativa de fachada/escola
```

### Mapeamento dos Protótipos para as Telas Finais de Produção:
| Arquivo de Protótipo (`frontend/test/`) | Página Final de Produção (`frontend/`) | Rota FastAPI | Papel no MVP |
|---|---|---|---|
| `test/login.html` | `frontend/index.html` | `GET /` | Tela pública de Login com identificador e senha |
| `test/cadastro.html` | `frontend/cadastro.html` | `GET /cadastro` | Tela de cadastro com dados pessoais, endereço e ViaCEP |
| `test/index.html` *(Painel Acadêmico)* | `frontend/home.html` | `GET /home` | Dashboard restrito exibindo dados do usuário e endereço |
| `test/recuperacao.html` | Mantido em `test/` | — | Rascunho demonstrativo; recuperação por e-mail é recurso pós-MVP |

---

## 5. Próxima Etapa de Execução

1. Criar o arquivo `frontend/static/css/style.css` com a identidade visual institucional e componentes responsivos (baseados na paleta azul/dourada dos protótipos).
2. Implementar `frontend/index.html` (Login) e `frontend/cadastro.html` (Cadastro) com formulários semânticos e validações.
3. Implementar `frontend/home.html` com o painel acadêmico e guarda de rota de sessão.
4. Implementar os scripts JavaScript em `frontend/static/js/`.
5. Testar o fluxo completo de ponta a ponta no navegador em `http://localhost:8000`.
