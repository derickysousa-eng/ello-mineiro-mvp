# Guia Passo a Passo: Cadastro de Usuário Guiado e Homologação de Dados Sintéticos

> **Finalidade:** Roteiro prático para testes de homologação, treinamento e demonstração ao vivo perante a banca avaliadora do projeto **Escola Particular Ello Mineiro — MVP**.  
> **Conformidade LGPD:** Para demonstrações públicas, **nunca utilize dados de pessoas físicas reais**. Este guia lista ferramentas homologadas que geram dados sintéticos (fictícios), mas que obedecem rigidamente às regras matemáticas e algorítmicas oficiais exigidas pelo sistema.

---

## 1. Ferramentas Homologadas para Geração de Dados Fictícios

Para simular o fluxo completo de cadastro com dados válidos, utilize as ferramentas abertas abaixo:

| Dado Cadastral | Ferramenta Recomendada | Link de Acesso | Particularidade Técnica no Sistema |
|---|---|---|---|
| **CPF (Válido)** | **4Devs** | [4devs.com.br/gerador_de_cpf](https://www.4devs.com.br/gerador_de_cpf) | O gerador calcula os dois dígitos verificadores via **Módulo 11**, exatamente como detalhado em [algoritmo-validacao-cpf.md](algoritmo-validacao-cpf.md). Se desejar simular emissão em MG, gere um CPF cujo 9º dígito seja **6**. |
| **RG (Conforme Estado)** | **4Devs** | [4devs.com.br/gerador_de_rg](https://www.4devs.com.br/gerador_de_rg) | Permite selecionar o estado de emissão (ex: Minas Gerais - MG). O sistema aceita de 7 a 13 caracteres alfanuméricos úteis com máscara dinâmica progressiva. |
| **CEP (Endereço Real)** | **4Devs** | [4devs.com.br/gerador_de_cep](https://www.4devs.com.br/gerador_de_cep) | Permite escolher estado (MG) e cidade (ex: Belo Horizonte). O CEP gerado é válido nos Correios e aciona o autopreenchimento imediato via **ViaCEP**. |
| **Telefone / Celular** | **Gerador NV** | [geradornv.com.br/gerador-telefone](https://geradornv.com.br/gerador-telefone/) | Permite selecionar o estado (ex: MG - DDD 31). O sistema formata dinamicamente entre telefone fixo (10 dígitos) e celular (11 dígitos). |

---

## 2. Roteiro de Cadastro Guiado Passo a Passo (`/cadastro`)

Acesse a página de cadastro na URL da aplicação:
* **Produção:** `https://<seu-app-render>.onrender.com/cadastro`
* **Local:** `http://localhost:8000/cadastro`

---

### Etapa 1: Credenciais de Acesso (Seção 1)

1. **Nome de Usuário (`user_login`):**
   * *Exemplo:* `marcos.oliveira` ou `aluna_mariana`
   * *Regra do Sistema:* Aceita entre 3 e 30 caracteres (`a-z`, `0-9`, ponto `.` ou sublinhado `_`). O sistema valida o formato em tempo real e preserva a escrita digitada.
2. **E-mail Institucional ou Pessoal (`email`):**
   * *Exemplo:* `marcos.oliveira@exemplo.com`
   * *Regra do Sistema:* O campo valida em tempo real a presença do `@` e do provedor/domínio. Se o formato estiver incorreto, exibe aviso orientador amigável.
3. **Senha de Acesso (`senha`):**
   * *Exemplo:* `SenhaSegura2026!`
   * *Regra do Sistema:* Mínimo de 8 caracteres. O **medidor de força** integrado analisa em tempo real a entropia (letras maiúsculas, minúsculas, números e símbolos especiais), mudando a barra de vermelho (fraca) para verde (forte).
4. **Confirmar Senha (`confirma_senha`):**
   * *Regra do Sistema:* Valida dinamicamente se as duas senhas coincidem antes do envio.

---

### Etapa 2: Dados Pessoais do Aluno / Usuário (Seção 2)

1. **Nome Completo (`nome`):**
   * *Exemplo digitado:* `marcos da silva oliveira junior`
   * *Recurso Title Case Inteligente:* Ao sair do campo (`blur`), o sistema formata automaticamente para `Marcos da Silva Oliveira Junior`, convertendo as iniciais para maiúsculas e preservando preposições em minúsculas (`da`, `de`, `do`, `dos`, `das`, `e`).
2. **Gênero (`genero`):**
   * Selecione uma das opções padronizadas do IBGE no menu suspenso (`Masculino`, `Feminino`, `Não-binário`, `Outro`, `Prefiro não informar`).
3. **Data de Nascimento (`data_nasc`):**
   * Selecione no seletor de calendário (ex: `2004-06-15`).
4. **CPF (`cpf` — Obrigatório):**
   * Gere um número no [Gerador de CPF da 4Devs](https://www.4devs.com.br/gerador_de_cpf).
   * Cole no campo. O sistema aplica a máscara automática `000.000.000-00` e calcula os dígitos verificadores pelo **Módulo 11** instantaneamente, exibindo borda verde e a mensagem *"CPF válido"*.
5. **RG (`rg` — Obrigatório):**
   * Gere um RG no [Gerador de RG da 4Devs](https://www.4devs.com.br/gerador_de_rg) (ou digite um modelo como `MG-18.492.301`).
   * A máscara dinâmica ajusta a pontuação conforme o padrão do estado informado.
6. **Telefone Celular Principal (`telefone`):**
   * Gere um número com DDD 31 no [Gerador de Telefone](https://geradornv.com.br/gerador-telefone/) (ex: `(31) 98765-4321`).
   * A máscara adapta automaticamente a pontuação ao detectar o nono dígito.
7. **Telefone Secundário / Recado (`telefone_sec` — Opcional):**
   * Campo opcional para contato de responsáveis ou telefone fixo residencial.

---

### Etapa 3: Endereço Residencial Obrigatório com ViaCEP (Seção 3)

1. **CEP (`cep`):**
   * Gere um CEP de Minas Gerais no [Gerador de CEP da 4Devs](https://www.4devs.com.br/gerador_de_cep) (ex: `30130-100` — Praça Sete de Setembro, Centro, Belo Horizonte/MG).
   * Digite os 8 dígitos no campo.
2. **Autopreenchimento Automático (API ViaCEP):**
   * Assim que o 8º dígito é inserido, o front-end dispara uma consulta assíncrona ao serviço nacional dos Correios (`viacep.com.br`).
   * Os campos **Logradouro/Rua**, **Bairro**, **Cidade** e **Estado (UF)** são preenchidos automaticamente em milissegundos e bloqueados para evitar erros de digitação.
   * O cursor é colocado automaticamente no campo **Número**.
3. **Número e Complemento:**
   * Preencha o número residencial (ex: `150`) e o complemento opcional (ex: `Apto 402`).

> **Contingência Automática de Rede:** Se o CEP digitado não for encontrado ou se os servidores do ViaCEP estiverem temporariamente fora do ar, o sistema emite um aviso orientador e **desbloqueia imediatamente todos os campos de endereço** para que o usuário faça o preenchimento manual sem ser impedido de prosseguir.

---

### Etapa 4: Aceite de Termos e Conclusão (Seção 4)

1. Marque a caixa de seleção: **"Li e concordo com os Termos e Condições de Uso"**.
2. Clique no botão **"Concluir Cadastro"**.
3. O botão exibirá um indicador de carregamento (*spinner* com "Processando Cadastro...").
4. Ao concluir, uma barra verde de notificação confirmará o sucesso e o navegador será redirecionado para a tela de Login (`/`) em 1,5 segundo.

---

## 3. Roteiro de Demonstração de Resiliência para a Banca

Durante a apresentação acadêmica, demonstrar cenários de erro e como o sistema se recupera transmite alto profissionalismo técnico. Sugerimos os seguintes testes rápidos:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   TESTES DE RESILIÊNCIA PARA APRESENTAÇÃO                   │
├──────────────────────────┬──────────────────────────────────────────────────┤
│ Cenário Demonstrado      │ Comportamento Esperado do Sistema                │
├──────────────────────────┼──────────────────────────────────────────────────┤
│ 1. CPF Inválido          │ Digite um CPF gerado e altere o último dígito.   │
│                          │ O sistema exibe borda vermelha e "CPF inválido". │
│                          │ Ao submeter, o envio é barrado localmente.       │
├──────────────────────────┼──────────────────────────────────────────────────┤
│ 2. E-mail sem @ ou ponto │ Digite "alunoteste" no campo de e-mail.          │
│                          │ O sistema avisa que o formato é incorreto e      │
│                          │ impede o envio com mensagem em português claro.  │
├──────────────────────────┼──────────────────────────────────────────────────┤
│ 3. Senhas Divergentes    │ Digite senhas diferentes nos dois campos.        │
│                          │ O campo de confirmação exibe feedback vermelho   │
│                          │ imediato: "As senhas não coincidem".             │
├──────────────────────────┼──────────────────────────────────────────────────┤
│ 4. Tentativa de Registro │ Tente cadastrar duas vezes o mesmo usuário ou    │
│    Duplicado             │ CPF. O backend responde com HTTP 409 Conflict:   │
│                          │ "Já existe um cadastro com este user_login/cpf". │
└──────────────────────────┴──────────────────────────────────────────────────┘
```

---

## 4. Validação Pós-Cadastro no Painel Acadêmico (`/home`)

1. Na tela de login (`/`), insira o **Nome de Usuário** (ou e-mail) e a **Senha** cadastrados.
2. O sistema realiza a autenticação, recebe o cookie seguro `HttpOnly` e redireciona para o Dashboard (`/home`).
3. No painel, confirme:
   * O nome próprio formatado em Title Case no cabeçalho e na saudação.
   * Os dados de **CPF** e **RG** devidamente protegidos com asteriscos centrais para preservar a privacidade do aluno na tela (ex: `123.***.***-01` e `MG-18.***-1`).
   * O endereço completo exibido no card de localização.
   * O perfil inicial atribuído automaticamente como **"Usuário"** e o menu de solicitação de permissão institucional.
