---
kanban-plugin: board
---

## Backlog

- [ ] Testes de usabilidade e responsividade completa (Mobile, Tablet, Desktop) #frontend
- [ ] Criação e homologação do cluster no TiDB Cloud Serverless (MySQL em nuvem) #banco #producao
- [ ] Configuração de deploy único no Render (FastAPI servindo front e API na mesma URL) #deploy #producao
- [ ] Validação de ponta a ponta em produção com HTTPS e cookie `Secure=True` #seguranca
- [ ] Regras Pós-MVP: Painel administrativo para atribuição de perfis (Aluno, Professor) e matrícula (doc 03) #futuro


## A fazer

- [ ] Decisão sobre obrigatoriedade de CPF e RG (avaliar NOT NULL vs LGPD e exceções de imigrantes) #banco #backend
- [ ] Criação da folha de estilos unificada institucional (`frontend/static/css/style.css`) #frontend #css
- [ ] Implementação da Tela de Login (`frontend/index.html`) adaptando layout de `frontend/test/login.html` #frontend
- [ ] Implementação da Tela de Cadastro (`frontend/cadastro.html`) adaptando `frontend/test/cadastro.html` #frontend
- [ ] Máscaras dinâmicas de telefone (fixo 10 dígitos / celular 11 dígitos) e CEP/CPF no front-end #frontend #js
- [ ] Integração com serviço ViaCEP para autopreenchimento de endereço no cadastro #frontend #js
- [ ] Validação interativa em tempo real com algoritmo de CPF (módulo 11) e força de senha #frontend #js
- [ ] Implementação do Dashboard (`frontend/home.html`) adaptando `frontend/test/index.html` #frontend
- [ ] Lógica de Route Guard no front-end: redirecionar para `/` se `/api/me` retornar 401 #frontend #js


## Em andamento

- [ ] Centralização e acompanhamento do fluxo de desenvolvimento via quadro Kanban #gestao


## Feito

**Complete**
- [x] Modelagem do banco MySQL (`database/seed.sql`) com tabelas Permissoes, Usuarios e Endereco #banco
- [x] Carga inicial de permissões institucionais e regra de perfil padrão 'Usuario' #banco
- [x] Integridade atômica usuário-endereço: impedimento de endereços órfãos e usuários sem endereço (RN04 / RNF19) #banco #backend
- [x] Backend FastAPI estruturado com SQL puro e queries parametrizadas (`PyMySQL`) sem ORM #backend
- [x] Hash seguro de senhas com Argon2id e emissão de JWT em cookie `HttpOnly; SameSite=Lax` #seguranca
- [x] Rotas de autenticação (`/api/auth/register`, `/api/auth/login`, `/api/auth/logout`) e leitura (`/api/me`, `/health`) #backend
- [x] Suporte a campos cadastrais opcionais nulos (`genero`, `cpf`, `rg`, `data_nasc`, `telefones`) #backend
- [x] Title Case inteligente para nomes (preservando preposições em minúsculas) e preservação de case no login #backend
- [x] Proteção de mutabilidade com `X-API-Key` para integrações externas e validação de mesma origem transparente para o site (RNF18) #seguranca
- [x] Rate Limiting por IP em memória (Sliding Window) com HTTP 429 Too Many Requests e header `Retry-After` (RNF07) #seguranca
- [x] Bateria automatizada de testes locais com 11 cenários de segurança e integridade (`test_api.py`) #testes
- [x] Exportação e sincronização da Postman Collection oficial com autenticação X-API-Key #docs
- [x] Inclusão e catálogo dos protótipos e referências visuais da equipe em `frontend/test/` #frontend
- [x] Especificação arquitetural completa e detalhada da interface web em `docs/05-modelagem-frontend.md` #docs


%% kanban:settings
```
{"kanban-plugin":"board","list-collapse":[false,false,false,false]}
```
%%
