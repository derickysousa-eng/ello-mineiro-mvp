# Algoritmo Oficial de Validação do CPF: Fundamentação Matemática, Especificação e Aplicação

> **Finalidade:** Material de consulta técnica e apoio acadêmico para apresentação do projeto **Escola Particular Ello Mineiro — MVP**.  
> **Tema:** Validação algorítmica de integridade do Cadastro de Pessoas Físicas (CPF).

---

## 1. O que é o CPF e sua Estrutura Anatômica

O **Cadastro de Pessoas Físicas (CPF)** é o registro mantido pela **Secretaria da Receita Federal do Brasil (RFB)** para identificar os contribuintes. O número é composto por exatamente **11 dígitos decimais**, tradicionalmente formatados como:

$$\mathbf{ABC.DEF.GHI - JK}$$

O número é subdividido em três seções lógicas:

| Seção | Dígitos | Papel no Documento |
|---|---|---|
| **Número-Base** | `ABC.DEF.GH` (8 primeiros) | Número sequencial de registro gerado no momento da inscrição. |
| **Região Fiscal** | `I` (9º dígito) | Código que identifica a Região Fiscal de origem da emissão do documento. |
| **Dígitos Verificadores (DV)** | `JK` (10º e 11º dígitos) | Dígitos de controle calculados matematicamente sobre os 9 anteriores via **Módulo 11**. |

### Tabela Oficial de Regiões Fiscais (9º Dígito)
A Receita Federal do Brasil organiza o território nacional em 10 Regiões Fiscais:
* **`1`**: Distrito Federal, Goiás, Mato Grosso, Mato Grosso do Sul e Tocantins
* **`2`**: Acre, Amazonas, Amapá, Pará, Rondônia e Roraima
* **`3`**: Ceará, Maranhão e Piauí
* **`4`**: Alagoas, Paraíba, Pernambuco e Rio Grande do Norte
* **`5`**: Bahia e Sergipe
* **`6`**: **Minas Gerais (MG)**
* **`7`**: Espírito Santo e Rio de Janeiro
* **`8`**: São Paulo (SP)
* **`9`**: Paraná e Santa Catarina
* **`0`**: Rio Grande do Sul (RS)

> *Exemplo Acadêmico:* Se um CPF tem o nono dígito igual a `6` (ex: `***.***.*6*-**`), a emissão original ocorreu na jurisdição de Minas Gerais.

---

## 2. O Algoritmo Homologado: Módulo 11 com Pesos Decrescentes

O algoritmo utilizado pela Receita Federal baseia-se no método clássico de **Soma Ponderada com Módulo 11**, amplamente empregado na ciência da computação e em sistemas bancários para detecção de erros em códigos numéricos.

### 2.1. Cálculo do Primeiro Dígito Verificador ($J$)

1. Multiplicam-se os **9 primeiros dígitos** por pesos decrescentes que variam de **10 até 2**:
   $$\text{Soma}_1 = (A \times 10) + (B \times 9) + (C \times 8) + (D \times 7) + (E \times 6) + (F \times 5) + (G \times 4) + (H \times 3) + (I \times 2)$$

2. Calcula-se o resto da multiplicação por 10 dividido por 11:
   $$\text{Resto}_1 = (\text{Soma}_1 \times 10) \pmod{11}$$

3. **Regra de Definição do Dígito $J$:**
   * Se $\text{Resto}_1 = 10$ ou $\text{Resto}_1 = 11$, o dígito $J$ será **`0`**.
   * Caso contrário, o dígito $J$ será o próprio valor de **$\text{Resto}_1$**.

---

### 2.2. Cálculo do Segundo Dígito Verificador ($K$)

1. Para o segundo dígito, considera-se agora os **10 dígitos** (os 9 dígitos originais acrescidos do dígito $J$ calculado no passo anterior). Os pesos decrescem de **11 até 2**:
   $$\text{Soma}_2 = (A \times 11) + (B \times 10) + (C \times 9) + (D \times 8) + (E \times 7) + (F \times 6) + (G \times 5) + (H \times 4) + (I \times 3) + (J \times 2)$$

2. Calcula-se o resto da multiplicação por 10 dividido por 11:
   $$\text{Resto}_2 = (\text{Soma}_2 \times 10) \pmod{11}$$

3. **Regra de Definição do Dígito $K$:**
   * Se $\text{Resto}_2 = 10$ ou $\text{Resto}_2 = 11$, o dígito $K$ será **`0`**.
   * Caso contrário, o dígito $K$ será o próprio valor de **$\text{Resto}_2$**.

---

### 2.3. Exemplo Prático Passo a Passo

Tomemos como exemplo hipotético os 9 primeiros dígitos: **`123.456.789`**.

#### Cálculo do 1º Dígito ($J$):
$$\begin{aligned}
\text{Soma}_1 &= (1 \times 10) + (2 \times 9) + (3 \times 8) + (4 \times 7) + (5 \times 6) + (6 \times 5) + (7 \times 4) + (8 \times 3) + (9 \times 2) \\
&= 10 + 18 + 24 + 28 + 30 + 30 + 28 + 24 + 18 = 210 \\
\text{Resto}_1 &= (210 \times 10) \pmod{11} = 2100 \pmod{11} = 10 \implies J = \mathbf{0}
\end{aligned}$$

#### Cálculo do 2º Dígito ($K$ com $J=0$):
$$\begin{aligned}
\text{Soma}_2 &= (1 \times 11) + (2 \times 10) + (3 \times 9) + (4 \times 8) + (5 \times 7) + (6 \times 6) + (7 \times 5) + (8 \times 4) + (9 \times 3) + (0 \times 2) \\
&= 11 + 20 + 27 + 32 + 35 + 36 + 35 + 32 + 27 + 0 = 255 \\
\text{Resto}_2 &= (255 \times 10) \pmod{11} = 2550 \pmod{11} = 9 \implies K = \mathbf{9}
\end{aligned}$$

* **Resultado Calculado:** `123.456.789-09`.

---

### 2.4. A Regra de Exclusão de Dígitos Repetidos

Um detalhe matemático crucial: sequências formadas por 11 dígitos repetidos (`000.000.000-00`, `111.111.111-11`, ..., `999.999.999-99`) geram somas proporcionais que coincidem com os próprios dígitos, passando matematicamente pelo teste do Módulo 11.

No entanto, a Receita Federal **invalida expressamente essas sequências**. Portanto, qualquer algoritmo homologado deve conter uma verificação preliminar rejeitando números repetidos:
```javascript
// Rejeita sequências conhecidas de dígitos repetidos
if (/^(\d)\1{10}$/.test(cpfLimpo)) return false;
```

---

## 3. Onde Encontrar a Especificação Homologada?

A regra matemática de formação e validação do CPF é **aberta, pública e padronizada** pelos seguintes órgãos oficiais:

1. **Receita Federal do Brasil (Ministério da Fazenda):**
   * **Instrução Normativa RFB nº 1.548/2015** e **IN RFB nº 2.172/2023**: Regulamentam os atos cadastrais do CPF perante a administração pública federal.
2. **SERPRO (Serviço Federal de Processamento de Dados):**
   * Manuais técnicos das APIs corporativas de consulta à base governamental e documentação oficial de interoperabilidade do portal `gov.br`.
3. **Padrão W3C Brasil:**
   * Diretrizes do escritório brasileiro do consórcio W3C para validação de dados em formulários eletrônicos nacionais.

---

## 4. O Algoritmo Abrange Todas as Possibilidades de CPF?

**Sim, ele abrange 100% de todos os CPFs já emitidos e que ainda serão emitidos no território nacional.**

No entanto, é fundamental para a apresentação acadêmica dominar a diferença técnica entre **Validação Sintática** e **Validação Cadastral**:

```
                  ┌───────────────────────────────────────────────┐
                  │            VALIDAÇÃO DO DOCUMENTO             │
                  └───────────────────────┬───────────────────────┘
                                          │
            ┌─────────────────────────────┴─────────────────────────────┐
            ▼                                                           ▼
┌───────────────────────────────────────┐   ┌─────────────────────────────────────────┐
│     Validação Sintática / Lógica      │   │     Validação Cadastral / Semântica     │
├───────────────────────────────────────┤   ├─────────────────────────────────────────┤
│ • Verifica a coerência matemática.    │   │ • Consulta a base central da Receita.   │
│ • Rejeita erros de digitação e fraudes│   │ • Verifica se a pessoa física existe.   │
│   óbvias instantaneamente.            │   │ • Retorna situação (Regular, Suspensa). │
│ • Custo computacional zero (0 ms).    │   │ • Paga por requisição (APIs Serpro).    │
│ • Opera OFFLINE (cliente e servidor). │   │ • Exige conexão online externa e token. │
└───────────────────────────────────────┘   └─────────────────────────────────────────┘
```

* **No nosso MVP:** Implementamos a **Validação Sintática Completa** (Módulo 11 + rejeição de repetidos) no Front-end e no Backend. Isso impede que números fictícios ou erros de digitação entrem no banco de dados.

---

## 5. Por que Incluir Essa Validação é Considerado uma Boa Prática?

Na engenharia de software corporativa, implementar essa validação é um **padrão de excelência mandatário** pelos seguintes motivos:

1. **Prevenção Imediata de Falhas na Experiência do Usuário (UX):**
   * Detecta que o usuário inverteu um número ou errou um dígito no exato momento da digitação, antes de submeter formulários extensos.
2. **Higienização e Integridade Referencial do Banco de Dados:**
   * A coluna `cpf CHAR(11) NOT NULL UNIQUE` armazena exclusivamente chaves íntegras. Isso evita poluicão com sequências aleatórias (`12345678900`) e impede que cadastros de teste quebrem funcionalidades futuras (emissão de contratos, diplomas, notas fiscais ou boletos bancários).
3. **Estratégia de Dupla Camada (Defense in Depth):**
   * **No Front-end (`auth.js`):** Validação interativa sem requisição de rede para melhor ergonomia do usuário.
   * **No Backend (`schemas.py`):** Validação matemática obrigatória que bloqueia clientes externos maliciosos que tentem burlar o formulário enviando payloads inválidos via Postman ou cURL, respondendo com **`HTTP 422 Unprocessable Entity`**.

---

## 6. Roteiro Prático de Explicação para Apresentação em Grupo

Ao apresentar este tópico aos professores e à banca avaliadora, sugerimos estruturar a fala em três blocos:

1. **Apresentação do Problema:**
   > *"Para garantir que o banco de dados escolar receba dados confiáveis e sem lixo cadastral, decidimos que o CPF não seria um simples campo de texto livre, mas sim um identificador validado matematicamente."*
2. **A Solução Técnica:**
   > *"Utilizamos o algoritmo oficial homologado pela Receita Federal, o Módulo 11 com pesos decrescentes de 10 a 2 e de 11 a 2. Ele confere os dois últimos dígitos verificadores do documento e rejeita sequências repetidas como 111.111.111-11."*
3. **A Arquitetura de Defesa em Duas Camadas:**
   > *"Essa validação não fica restrita à interface: ela opera no navegador em JavaScript para dar feedback instantâneo ao usuário e é repetida com rigor no backend FastAPI via Pydantic, garantindo que mesmo requisições externas via API sejam barradas caso o documento seja matematicamente inválido."*
