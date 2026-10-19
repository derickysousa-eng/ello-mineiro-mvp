---

kanban-plugin: board

---

## Backlog

- [ ] Testes de usabilidade e responsividade completa (Mobile, Tablet, Desktop) #frontend
- [ ] Regras Pós-MVP: Painel administrativo para atribuição de perfis (Aluno, Professor) e matrícula (doc 03) #futuro
- [ ] Implementar fluxo de backend para envio de e-mail e validação de token em `frontend/recuperacao.html` #futuro #backend
- [ ] Implementar Soft Delete para Usuários (Data de Desligamento) #futuro
	
	Substituir a exclusão física (`DELETE`) de usuários pela exclusão lógica (_Soft Delete_). O objetivo é manter o histórico, garantir a integridade referencial do banco de dados (faturas, logs, etc.) e possibilitar auditorias futuras, alinhando-se às melhores práticas de sistemas corporativos (CRMs, ERPs).


## A fazer


## Em andamento


## Feito

- [x] Criação da branch `feature/refatoracao-poo` para evolução arquitetural do backend #git #poo
- [x] Implementação das classes de domínio puras `Usuario` e `Endereco` com Composição e Encapsulamento #backend #poo
- [x] Implementação das classes de repositório `UsuarioRepository` e `EnderecoRepository` com injeção de conexão #backend #poo
- [x] Implementação da camada de serviço `AuthService` desacoplando regras de negócio dos roteadores FastAPI #backend #poo
- [x] Validação de retrocompatibilidade total com a bateria de 11 testes automatizados (`test_api.py`) #testes #poo

- [x] Criação e homologação do cluster no TiDB Cloud Serverless (MySQL em nuvem AWS us-east-1) com TLS #banco #producao
- [x] Configuração de deploy único no Render (FastAPI servindo front e API na mesma URL) com segredos protegidos #deploy #producao
- [x] Validação de ponta a ponta em produção com HTTPS e cookie `Secure=True` #seguranca
- [x] Documentação técnica de apresentação da infraestrutura e segurança em `docs-apresentacao/infraestrutura-e-seguranca.md` #docs
- [x] Obrigatoriedade de CPF e RG (NOT NULL e UNIQUE) implementada no seed.sql, schemas Pydantic (módulo 11), front-end e testes #banco #backend #frontend
- [x] Centralização e acompanhamento do fluxo de desenvolvimento via quadro Kanban #gestao
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
- [x] Criação da folha de estilos unificada institucional (`frontend/static/css/style.css`) #frontend #css
- [x] Implementação da Tela de Login (`frontend/index.html`) com suporte a RF05 e feedback visual #frontend
- [x] Implementação da Tela de Cadastro (`frontend/cadastro.html`) com dados pessoais e endereço obrigatório #frontend
- [x] Validação interativa em tempo real com algoritmo de CPF (módulo 11) e medidor de força de senha #frontend #js
- [x] Integração com serviço ViaCEP para autopreenchimento de endereço e liberação manual de contingência #frontend #js
- [x] Máscaras dinâmicas de telefone (fixo 10 dígitos / celular 11 dígitos) e CEP/CPF no front-end #frontend #js
- [x] Implementação do Dashboard (`frontend/home.html`) exibindo dados completos do usuário e endereço #frontend
- [x] Lógica de Route Guard no front-end: validação de sessão em `GET /api/me` e logout seguro #frontend #js
- [x] Inclusão e refatoração da tela de Recuperação de Senha (`frontend/recuperacao.html` e rota `GET /recuperacao`) #frontend
- [x] Refatoração visual com biblioteca Bootstrap Icons eliminando emojis e profissionalizando a interface #frontend
- [x] Documentação detalhada da arquitetura do servidor e rotas em `docs/06-arquitetura-servidor-e-rotas.md` #docs




%% kanban:settings
```
{"kanban-plugin":"board","list-collapse":[false,false,false,false]}
```
%%