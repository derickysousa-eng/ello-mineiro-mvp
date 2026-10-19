# Arquitetura do Servidor, Entrega de Páginas e Centralização de Estilos (Front-end)

> Este documento explica detalhadamente a lógica empregada no ponto de entrada da aplicação (`app/main.py`), a estratégia de entrega dos arquivos estáticos pelo FastAPI, a centralização do design system em `frontend/static/css/style.css` e o fluxo de manutenção para atualizações futuras.

---

## 1. Visão Geral da Arquitetura de Mesma Origem (Zero CORS)

A aplicação adota o modelo de **Monólito Modular de Mesma Origem (Single-Origin Architecture)**. Em vez de hospedar o front-end em um servidor separado (como Node.js, Vercel ou Nginx) e o backend em outro, o próprio processo do **FastAPI** desempenha dois papéis simultâneos:
1. **API RESTful:** Fornece os endpoints de negócio sob o prefixo `/api` (`/api/auth/login`, `/api/auth/register`, `/api/auth/logout`, `/api/me`, `/health`).
2. **Servidor de Arquivos Estáticos e Páginas:** Entrega os documentos HTML5 e seus recursos complementares (CSS, JS, imagens).

### Vantagens Estratégicas desta Abordagem:
* **Zero CORS (*Cross-Origin Resource Sharing*):** Como páginas e APIs residem sob o mesmo esquema, domínio e porta (`http://127.0.0.1:8000`), o navegador nunca dispara requisições de pré-voo (`OPTIONS preflight`), reduzindo latência e eliminando vulnerabilidades de cabeçalhos permissivos.
* **Segurança Nativa de Sessão com Cookies HttpOnly:** O cookie de autenticação `access_token` é anexado automaticamente pelo navegador em todas as chamadas para a mesma origem, sem necessidade de JavaScript injetar cabeçalhos `Authorization: Bearer` ou armazenar tokens no `localStorage`.
* **Handshake Transparente de Origem:** As chamadas do front-end contêm automaticamente os cabeçalhos `Sec-Fetch-Site: same-origin` e `Origin`, permitindo ao backend dispensar a exigência de chaves de API (`X-API-Key`) no navegador do cliente, mantendo essa chave exclusivamente para integrações de terceiros.

---

## 2. Lógica Empregada no `app/main.py`

O arquivo `app/main.py` foi estruturado de forma desacoplada e enxuta, dividindo responsabilidades com clareza:

### 2.1. Registro dos Roteadores da API
```python
# Registra os roteadores de autenticação e perfil sob o prefixo /api
app.include_router(auth_router, prefix="/api")
app.include_router(me_router, prefix="/api")
```
* **Isolamento de Domínio:** Todas as rotas de negócio trafegam estritamente sob o namespace `/api/`, garantindo que requisições de dados não colidam com rotas de visualização web.

### 2.2. Montagem de Recursos Estáticos (`StaticFiles`)
```python
frontend_static_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "static")
if os.path.exists(frontend_static_dir):
    app.mount("/static", StaticFiles(directory=frontend_static_dir), name="static")
```
* **Resolução de Caminhos Absolutos:** O uso de `os.path.dirname(__file__)` garante que o servidor localize os arquivos independentemente de onde o comando de inicialização (`uvicorn`) for disparado no terminal.
* **Cache e Performance:** O Starlette/FastAPI cuida automaticamente dos cabeçalhos de *Content-Type* (`text/css`, `application/javascript`, `image/png`) e de validação de cache HTTP (*ETag*, *Last-Modified*).

### 2.3. Rotas de Páginas HTML (`FileResponse`)
```python
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")

@app.get("/", include_in_schema=False)
def pagina_login():
    """Retorna a tela pública de Login."""
    caminho = os.path.join(frontend_dir, "index.html")
    if os.path.exists(caminho):
        return FileResponse(caminho)
    return {"mensagem": "Página de login em construção."}

@app.get("/cadastro", include_in_schema=False)
def pagina_cadastro():
    """Retorna a tela de Cadastro de Usuário."""
    caminho = os.path.join(frontend_dir, "cadastro.html")
    if os.path.exists(caminho):
        return FileResponse(caminho)
    return {"mensagem": "Página de cadastro em construção."}

@app.get("/home", include_in_schema=False)
def pagina_home():
    """Retorna o Painel Acadêmico / Dashboard."""
    caminho = os.path.join(frontend_dir, "home.html")
    if os.path.exists(caminho):
        return FileResponse(caminho)
    return {"mensagem": "Página inicial em construção."}

@app.get("/recuperacao", include_in_schema=False)
def pagina_recuperacao():
    """Retorna a tela de Recuperação de Senha."""
    caminho = os.path.join(frontend_dir, "recuperacao.html")
    if os.path.exists(caminho):
        return FileResponse(caminho)
    return {"mensagem": "Página de recuperação em construção."}
```
* **`include_in_schema=False`:** Oculta rotas de visualização da documentação interativa OpenAPI/Swagger (`/docs`), mantendo o Swagger focado estritamente nas rotas de API pública e contratos JSON.
* **`FileResponse`:** O Starlette faz o streaming eficiente do arquivo HTML do disco diretamente para o fluxo de saída do cliente sem carregar todo o arquivo desnecessariamente em memória RAM.

---

## 3. Centralização dos Estilos: O Arquivo `frontend/static/css/style.css`

Toda a identidade visual, responsividade, formulários e componentes visuais do projeto são geridos centralizadamente em um único arquivo: **`frontend/static/css/style.css`**.

### 3.1. Arquitetura de Design Tokens (Variáveis CSS)
No início do arquivo, o seletor `:root` declara a paleta corporativa e métricas visuais da instituição:
```css
:root {
  /* Identidade Oficial Ello Mineiro */
  --color-primary: #1A365D;       /* Azul Profundo */
  --color-primary-dark: #0F2341;
  --color-primary-light: #2A4D80;
  --color-gold: #CFAD6D;          /* Dourado Nobre */
  --color-gold-hover: #BF9B55;
  --color-gold-light: #F4EAD4;
  
  /* Superfícies e Tipografia */
  --bg-body: #10243E;
  --bg-card: #FFFFFF;
  --bg-surface: #F8F9FA;
  --text-main: #1A202C;
  --text-muted: #718096;
  
  /* Status Semânticos */
  --color-success: #2E7D32;
  --color-error: #D32F2F;
  --color-warning: #ED6C02;
  
  /* Raios e Sombras */
  --border-radius-md: 10px;
  --border-radius-lg: 16px;
  --shadow-lg: 0 12px 28px rgba(16, 36, 62, 0.25);
}
```

### 3.2. Como as Páginas Compartilham o CSS
Todas as páginas HTML (`index.html`, `cadastro.html`, `home.html`, `recuperacao.html`) importam exatamente a mesma folha de estilos:
```html
<link rel="stylesheet" href="/static/css/style.css">
```
Isso garante:
1. **Consistência Visual Imediata:** Um botão `.btn-primary` ou um campo `.form-input` possui comportamento, transição, bordas e foco idênticos em qualquer tela do portal.
2. **Reaproveitamento de Cache no Navegador:** Uma vez que o usuário carrega a tela de login, o arquivo `style.css` fica armazenado no cache local do navegador, tornando o carregamento das páginas seguintes (`/cadastro`, `/home`, `/recuperacao`) instantâneo (0 ms de download de estilos).

### 3.3. Como Realizar Atualizações Futuras no CSS com Segurança
Para alterar cores, fontes, tamanhos ou criar novos componentes sem gerar regressões:
* **Alterar Tokens Globais:** Se a escola decidir alterar a cor dourada de `#CFAD6D` para outro tom, basta modificar a variável `--color-gold` no `:root` de `style.css`. **Todas as telas serão atualizadas automaticamente de uma única vez**.
* **Adicionar Novos Componentes:** Crie a classe sob uma nomenclatura semântica (ex: `.card-boletim`, `.tabela-notas`) mantendo o uso das variáveis (`var(--color-primary)`, `var(--border-radius-md)`).
* **Evitar Estilos Inline nos Arquivos HTML:** Nunca inclua tags `<style>` repetitivas dentro dos arquivos `.html`; utilize sempre as classes documentadas em `style.css`.

---

## 4. Biblioteca de Ícones Profissionais (Bootstrap Icons)

Para garantir uma interface profissional sem emojis nos rótulos de botões e cartões, o portal utiliza a biblioteca **Bootstrap Icons** via CDN oficial:
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
```
* **Independência Total de Frameworks:** Não requer React, Vue, jQuery ou pacotes Node.js/npm. É puramente CSS vetorial (SVG Webfonts).
* **Classes Semânticas Padronizadas:**
  * `<i class="bi bi-box-arrow-in-right"></i>`: Submissão de Login.
  * `<i class="bi bi-person-plus-fill"></i>`: Link para Cadastro.
  * `<i class="bi bi-eye"></i>` / `<i class="bi bi-eye-slash"></i>`: Alternância de visibilidade da senha.
  * `<i class="bi bi-key-fill"></i>`: Recuperação de senha.
  * `<i class="bi bi-house-door-fill"></i>`, `<i class="bi bi-calendar3"></i>`, `<i class="bi bi-bar-chart-fill"></i>`: Navegação lateral do dashboard.
  * `<i class="bi bi-box-arrow-left"></i>`: Encerramento de sessão (Logout).

---

## 5. Resumo do Mapa de Rotas e Telas de Produção

| Rota no Navegador | Método | Função no `app/main.py` | Arquivo Físico Servido | Propósito |
|---|---|---|---|---|
| `/` | `GET` | `pagina_login()` | `frontend/index.html` | Tela de Login com suporte a usuário ou e-mail (RF05) |
| `/cadastro` | `GET` | `pagina_cadastro()` | `frontend/cadastro.html` | Cadastro completo com dados pessoais, ViaCEP e termos |
| `/home` | `GET` | `pagina_home()` | `frontend/home.html` | Dashboard acadêmico protegido por sessão e Route Guard |
| `/recuperacao` | `GET` | `pagina_recuperacao()` | `frontend/recuperacao.html` | Tela informativa e formulário de recuperação de senha |
| `/static/*` | `GET` | `StaticFiles` | `frontend/static/*` | CSS unificado, scripts JS (`auth.js`, `home.js`), logotipos |
