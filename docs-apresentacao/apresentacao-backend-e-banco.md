# Apresentação do Backend e Banco de Dados: Do SQL Puro às Rotas de API

> **Finalidade:** Roteiro técnico e material de apoio para a apresentação acadêmica do projeto **Escola Particular Ello Mineiro — MVP**.  
> **Foco:** Arquitetura do Backend em Python/FastAPI, Engenharia de Banco de Dados Relacional (MySQL / TiDB Cloud), Operações CRUD, Transações Atômicas e Comunicação de Ponta a Ponta com o Front-end.

---

## 1. A Grande Analogia: O Restaurante da Computação

Para explicar de forma simples e memorável como o sistema opera por baixo dos panos, usamos a clássica analogia do **Restaurante de Alta Gastronomia**:

```
 ┌──────────────────────┐           ┌──────────────────────┐           ┌──────────────────────┐           ┌──────────────────────┐
 │       O SALÃO        │           │       O GARÇOM       │           │      A COZINHA       │           │      A DESPENSA      │
 │     (Front-end)      │  ───────► │    (Rotas da API)    │  ───────► │  (Backend / FastAPI) │  ───────► │   (Banco de Dados)   │
 ├──────────────────────┤           ├──────────────────────┤           ├──────────────────────┤           ├──────────────────────┤
 │ O cliente folheia o  │           │ Leva a comanda com os│           │ O chefe inspeciona os│           │ Cofre com chave e    │
 │ cardápio e preenche o│           │ dados em formato JSON│           │ ingredientes, calcula│           │ temperatura estrita. │
 │ formulário na mesa.  │           │ seguro e padronizado.│           │ o Módulo 11 e hashes.│           │ Armazena com ACID.   │
 └──────────────────────┘           └──────────────────────┘           └──────────────────────┘           └──────────────────────┘
```

1. **O Salão (Front-end):** Onde o usuário está confortável, preenche seus dados no formulário e visualiza as informações de forma limpa.
2. **O Garçom (Rotas da API RESTful):** O mensageiro que transporta os pedidos. Ele leva as requisições em formato JSON (`POST /api/auth/register`) e traz de volta a resposta (`HTTP 201 Created` ou alertas de erro).
3. **A Cozinha (Backend FastAPI):** Onde as regras de negócio acontecem. O chefe verifica se os dados são frescos e limpos (validações do Pydantic), criptografa a senha com Argon2id e coordena a ordem de preparo.
4. **A Despensa / Cofre (Banco de Dados MySQL / TiDB Cloud):** O local seguro e permanente onde tudo é guardado com rígido controle de inventário (integridade referencial e transações atômicas).

---

## 2. A Engenharia do Banco de Dados Relacional (MySQL / TiDB Cloud)

O banco de dados foi modelado em SQL puro no arquivo [database/seed.sql](file:///c:/Users/israe/Documents/ESTUDOS%20PROGRAMA%C3%87%C3%83O%20WEB/projeto-grau-tec/ello-mineiro-mvp/database/seed.sql), composto por **3 tabelas relacionais estratégicas**:

```
 ┌─────────────────────────┐
 │       Permissoes        │
 ├─────────────────────────┤
 │ PK  nome_permissao      │◄───────┐
 │     descricao           │        │
 └─────────────────────────┘        │
                                    │ (1:N - FK permissao_nome)
 ┌─────────────────────────┐        │
 │        Usuarios         │        │
 ├─────────────────────────┤        │
 │ PK  id                  │        │
 │     user_login (UNIQUE) │        │
 │     email (UNIQUE)      │        │
 │     senha_hash          │        │
 │ FK  permissao_nome      │────────┘
 │     nome                │
 │     cpf (NOT NULL)      │
 │     rg (NOT NULL)       │
 │     data_nasc           │
 │     telefone            │
 │     ativo (BOOL)        │
 └────────────┬────────────┘
              │
              │ (1:N - FK usuario_id / ON DELETE CASCADE)
              ▼
 ┌─────────────────────────┐
 │        Endereco         │
 ├─────────────────────────┤
 │ PK  id                  │
 │ FK  usuario_id          │
 │     tipo (Residencial)  │
 │     cep (8 dígitos)     │
 │     rua, numero, bairro │
 │     complemento         │
 │     cidade, uf          │
 │     situacao (ATIVO)    │
 └─────────────────────────┘
```

### 2.1. O Princípio da Atomicidade ACID ("Tudo ou Nada")
* **O Risco Clássico:** Em sistemas mal projetados, se a internet cair enquanto um usuário é salvo no banco, o cadastro pode criar um "usuário fantasma" sem endereço, ou um "endereço órfão" sem dono.
* **Nossa Solução (Transação Atômica):** No módulo [app/routers/auth.py](file:///c:/Users/israe/Documents/ESTUDOS%20PROGRAMA%C3%87%C3%83O%20WEB/projeto-grau-tec/ello-mineiro-mvp/app/routers/auth.py#L97-L107), utilizamos o controle manual de transações:
  ```python
  try:
      novo_id = repo_usuarios.criar_usuario(conn, dados, senha_hash)
      repo_enderecos.criar_endereco(conn, novo_id, dados.endereco)
      conn.commit()  # Salva AMBOS juntos
  except Exception:
      conn.rollback()  # Se qualquer um falhar, DESFAZ tudo imediatamente
  ```
* **Analogia:** Como uma transferência bancária: ou o dinheiro sai de uma conta E entra na outra, ou a operação inteira é cancelada. Não existe meio-termo.

---

### 2.2. Particularidade Técnica de Nuvem: O AUTO_INCREMENT no TiDB (Alocação em Lotes / Batch Cache)
* **O Fenômeno Visual:** Ao executar `SELECT * FROM Usuarios;` no TiDB Cloud, nota-se que os IDs primários não seguem necessariamente a sequência contígua unitária (`1, 2, 3, 4`), apresentando saltos em blocos (ex: `1`, `30001`, `30002`, `30003`, `30004`, `60001`, `90001`).
* **Por que isso acontece?**
  * Em um **MySQL monolítico local** (como no XAMPP), uma única CPU gerencia a fila e entrega números de 1 em 1 através de travas (*locks*) de tabela.
  * O **TiDB Cloud é um banco NewSQL distribuído**. Para suportar alta escala e evitar que milhares de conexões disputem uma trava central lenta, o TiDB aloca blocos de IDs em cache para cada sessão ativa (por padrão, blocos de 30.000 números: `AUTO_ID_CACHE = 30000`).
  * **Comprovação prática:** Quando nossa bateria de testes automatizados ([test_api.py](file:///c:/Users/israe/Documents/ESTUDOS%20PROGRAMA%C3%87%C3%83O%20WEB/projeto-grau-tec/ello-mineiro-mvp/test_api.py)) rodou, ela recebeu uma faixa de lote e inseriu de forma perfeitamente consecutiva os IDs `30001`, `30002`, `30003` e `30004`. Conexões posteriores do Render receberam os blocos `60001` e `90001`.
* **Integridade Relacional Perfeita:** Isso **não é um erro**. Na modelagem de dados, a Chave Primária precisa ser exclusivamente **única e imutável**. O relacionamento 1:N com a tabela `Endereco` opera com 100% de integridade (o endereço do aluno 60001 aponta exatamente para `usuario_id = 60001`).
* **Destaque Acadêmico para a Apresentação:** Explicar esse comportamento perante a banca evidencia domínio avançado sobre arquitetura de dados distribuídos em nuvem.

---

## 3. Por Que Escolhemos SQL Puro com PyMySQL (Sem ORMs Pesados)?

Muitos projetos usam bibliotecas chamadas ORMs (como SQLAlchemy ou Prisma), que traduzem código Python em comandos SQL por baixo dos panos. 

Decidimos usar **SQL Puro com PyMySQL** pelos seguintes motivos fundamentais:

1. **Aderência Direta à Disciplina de Banco de Dados:** Demonstrar domínio técnico real da linguagem SQL, escrevendo comandos DDL (`CREATE TABLE`, `CONSTRAINTS`) e DML (`INSERT`, `SELECT`, `UPDATE`).
2. **Performance Extrema:** O SQL puro elimina camadas intermediárias de tradução, executando consultas com velocidade máxima.
3. **Prevenção Absoluta contra SQL Injection (Consultas Parametrizadas):**
   * *O que é SQL Injection?* É quando um invasor digita códigos maliciosos como `' OR '1'='1` em um campo de texto para tentar enganar o banco e vazar dados.
   * *Como neutralizamos 100% desse risco:* Nenhuma consulta é concatenada com texto puro. Usamos marcadores de parâmetros (`%s`):
     ```python
     # SEGURO: O driver PyMySQL envia o comando SQL separado dos dados
     cursor.execute(
         "SELECT * FROM Usuarios WHERE user_login = %s OR email = %s",
         (identificador, identificador)
     )
     ```
     O banco trata a entrada do usuário estritamente como dado inofensivo, nunca como código executável.

---

## 4. O Ciclo de Vida Completo de uma Requisição (Por Baixo dos Panos)

Quando o aluno clica no botão **"Concluir Cadastro"** na interface, veja a jornada de milissegundos que a informação percorre:

```
[ Front-end: Clique no Botão ]
             │
             ▼ 1. fetch POST em JSON
[ FastAPI: Roteador /api/auth/register ]
             │
             ▼ 2. Inspeção de Cabeçalhos (security_guards.py)
   Verifica se é o navegador oficial (Sec-Fetch-Site) ou exige X-API-Key.
   Verifica o Rate Limiter por IP (máximo 10 requisições por minuto).
             │
             ▼ 3. Validação Sintática Rigorosa (Pydantic / schemas.py)
   Recalcula o Módulo 11 do CPF. Valida se a senha tem 8+ caracteres.
   Valida o formato do e-mail. Se falhar, retorna HTTP 422 humanizado.
             │
             ▼ 4. Injeção de Conexão com o Banco (db.py - Depends(get_db))
   Abre o canal cifrado com o TiDB Cloud na nuvem via túnel TLS/SSL.
             │
             ▼ 5. Criptografia da Senha (security.py)
   Gera o hash irreversível da senha com Argon2id antes de tocar no disco.
             │
             ▼ 6. Camada de Repositórios e CRUD Atômico (usuarios.py + enderecos.py)
   Executa INSERT INTO Usuarios e INSERT INTO Endereco na mesma transação.
             │
             ▼ 7. Confirmação (conn.commit())
   O TiDB Cloud grava no armazenamento seguro distribuído.
             │
             ▼ 8. Resposta HTTP 201 Created
[ Front-end: Recebe Sucesso e Redireciona para o Login ]
```

---

## 5. Como o CRUD foi Exportado e Consumido no Front-end

O backend transforma as operações clássicas de banco de dados em **Endpoints de API RESTful**:

| Operação CRUD | Ação de Banco (SQL) | Endpoint da API | Método HTTP | Onde é Consumido no Front? |
|---|---|---|---|---|
| **CREATE** | `INSERT INTO Usuarios` e `Endereco` | `/api/auth/register` | `POST` | Botão "Concluir Cadastro" em `cadastro.html` |
| **READ** | `SELECT ... WHERE user_login/email` | `/api/auth/login` | `POST` | Botão "Entrar no Portal" em `index.html` |
| **READ** | `SELECT ... JOIN Endereco ON id` | `/api/me` | `GET` | Ao carregar `home.html` para preencher o perfil |
| **REVOKE** | Invalida o cookie de sessão | `/api/auth/logout` | `POST` | Botão "Encerrar Sessão" no menu de `home.html` |

---

## 6. Roteiro de Fala para a Apresentação (Pitch do Backend e Banco)

> *"Na camada de Backend e Banco de Dados, a nossa prioridade foi a robustez arquitetural e a proteção de dados.  
> Desenvolvemos a API em Python com FastAPI, sem utilizar ORMs automáticos ou caixas-pretas: escrevemos SQL puro e parametrizado com PyMySQL, garantindo controle total sobre as consultas e blindagem total contra SQL Injection.  
> O banco de dados foi modelado em 3 tabelas relacionais essenciais: Permissões, Usuários e Endereços.  
> Uma decisão de engenharia crítica foi a Atomicidade Total: o cadastro de um aluno grava o usuário e o seu endereço sob uma mesma transação bancária. Se qualquer detalhe falhar, o sistema desfaz a gravação, garantindo que nunca existam endereços órfãos ou usuários sem endereço no banco.  
> Do lado da segurança de autenticação, nunca gravamos senhas legíveis: utilizamos o algoritmo Argon2id e entregamos a sessão via Cookie HttpOnly, que impede que qualquer script externo roube a sessão do aluno.  
> Todo esse ecossistema opera hoje em produção contínua, conectando o Render ao cluster NewSQL do TiDB Cloud."*
