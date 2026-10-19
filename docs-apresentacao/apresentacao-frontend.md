# Apresentação do Front-end: Engenharia de Interface, UX e Filosofia Vanilla

> **Finalidade:** Roteiro técnico e material de apoio para a apresentação acadêmica do projeto **Escola Particular Ello Mineiro — MVP**.  
> **Foco:** Arquitetura do Front-end, Experiência do Usuário (UI/UX), Bibliotecas Utilizadas, Integrações com APIs Externas e Decisões de Design.

---

## 1. A Filosofia do Front-end: O Poder do "Vanilla" (Sem Frameworks Pesados)

### 💡 A Analogia do Carro de Corrida vs. Caminhão de Mudança
* Muitos desenvolvedores iniciantes usam frameworks pesados como React, Angular ou Next.js para fazer formulários simples. Isso é como **alugar um caminhão de mudança gigante para levar apenas uma mochila de escola**: consome muita memória, demora para carregar e introduz centenas de dependências frágeis.
* No projeto Ello Mineiro, escolhemos a abordagem **Vanilla (HTML5, CSS3 e JavaScript ES6+ puros)**:
  * Como um **carro esportivo sob medida**, nossa aplicação é extremamente leve, carrega quase instantaneamente (menos de 1 segundo), não quebra por versões de pacotes e roda nativamente em qualquer navegador moderno (Chrome, Edge, Safari, Firefox).

---

## 2. Identidade Visual e Design System Centralizado

A estética de um software educacional transmite credibilidade e seriedade institucional. Desenvolvemos uma folha de estilos unificada em [frontend/static/css/style.css](file:///c:/Users/israe/Documents/ESTUDOS%20PROGRAMA%C3%87%C3%83O%20WEB/projeto-grau-tec/ello-mineiro-mvp/frontend/static/css/style.css):

### Paleta de Cores Institucional e Design Tokens:
* **Azul Marinho Real (`#1A365D`):** Representa autoridade, segurança, tradição e foco acadêmico.
* **Dourado Nobre (`#CFAD6D`):** Utilizado em botões de ação primária (*Call to Action*), bordas de destaque e detalhes de acabamento, simbolizando excelência e valor.
* **Branco Neve e Cinzas Neutros (`#FFFFFF`, `#F8FAFC`, `#E2E8F0`):** Proporcionam respiro visual, conforto de leitura e clareza aos formulários.
* **Sem Emojis — Padrão Bootstrap Icons:** Eliminamos qualquer uso de emojis informais. Toda a iconografia da aplicação utiliza a biblioteca profissional **Bootstrap Icons** via CDN (ícones vetoriais em formato SVG de alta precisão).

---

## 3. As Tecnologias e Bibliotecas Empregadas

| Tecnologia / Recurso | Papel na Interface | Por que foi escolhida? |
|---|---|---|
| **HTML5 Semântico** | Estruturação de páginas (`<main>`, `<section>`, `<nav>`, `<label>`) | Garante acessibilidade (leitores de tela), semântica limpa e indexação correta para navegadores. |
| **CSS3 Puro com Variáveis** | Estilização responsiva e Design Tokens | Variáveis CSS centralizadas no `:root` facilitam a troca de temas ou ajustes em segundos em um único arquivo. |
| **JavaScript Nativo (ES6+)** | Lógica de validações, máscaras e comunicação assíncrona (`fetch`) | Alta performance sem intermediários, compatível com a arquitetura moderna da web. |
| **Bootstrap Icons CDN** | Iconografia vetorial institucional | Ícones nítidos em qualquer resolução de tela (Retina/Mobile), sem dependência de bibliotecas pesadas. |
| **API Externa ViaCEP** | Autopreenchimento assíncrono de endereços | Consulta direta à base oficial dos Correios, poupando o usuário de digitar 4 campos repetitivos. |
| **Google Fonts (Inter)** | Tipografia moderna e legível | Fonte de alta legibilidade adotada pelos maiores produtos digitais do mundo. |

---

## 4. A Lógica Inteligente do Cliente (`auth.js` e `home.js`)

Por trás da interface visual, o JavaScript executa regras refinadas de ergonomia e segurança em [frontend/static/js/auth.js](file:///c:/Users/israe/Documents/ESTUDOS%20PROGRAMA%C3%87%C3%83O%20WEB/projeto-grau-tec/ello-mineiro-mvp/frontend/static/js/auth.js):

### 4.1. Title Case Inteligente no Nome Próprio
* **O Problema:** Usuários frequentemente digitam o nome todo em minúsculas (`carlos da silva costa`) ou todo em maiúsculas (`CARLOS DA SILVA`).
* **A Solução:** Nossa função `formatarTitleCase` analisa cada palavra: capitaliza os nomes e mantém propositalmente preposições em minúsculas (`da`, `de`, `do`, `dos`, `das`, `e`), resultando em: `Carlos da Silva Costa`.

### 4.2. Máscaras Dinâmicas em Tempo Real
* **Telefone Adaptativo:** O campo identifica se o usuário está digitando um telefone fixo (10 dígitos: `(31) 3333-4444`) ou um celular com o 9º dígito (11 dígitos: `(31) 98888-7777`) e formata dinamicamente os parênteses e hífens.
* **Máscara Flexível de RG:** Aceita padrões estaduais brasileiros de 7 a 13 caracteres úteis (incluindo o estado do Rio Grande do Norte e dígitos verificadores 'X').
* **Máscara e Módulo 11 de CPF:** Enquanto o usuário digita, o CPF é formatado (`000.000.000-00`) e os dois dígitos verificadores são calculados matematicamente. Se o CPF for falso ou inventado, o campo exibe borda vermelha e aviso imediato.

### 4.3. Integração Assíncrona com a API do ViaCEP
* Ao completar 8 dígitos no campo CEP, o front-end dispara uma chamada em segundo plano (`fetch`) para o webservice nacional `https://viacep.com.br/ws/{cep}/json/`.
* Os campos de **Rua**, **Bairro**, **Cidade** e **Estado** são preenchidos em fração de segundos, e o foco do teclado pula automaticamente para o campo **Número**.
* **Mecanismo de Resiliência:** Caso o ViaCEP fique temporariamente fora do ar ou o usuário resida em área rural sem CEP específico, o sistema exibe aviso orientador e **desbloqueia os campos** para preenchimento manual, garantindo que o cadastro nunca trave.

### 4.4. Medidor de Força de Senha e Alternador Visual
* Uma barra dinâmica colorida calcula a entropia da senha com base no tamanho e variedade de caracteres (letras maiúsculas, minúsculas, números e caracteres especiais).
* O botão de "olhinho" permite ao usuário alternar a visualização da senha sem recarregar a tela.

### 4.5. Route Guard e Proteção de Privacidade no Dashboard (`home.js`)
* Ao carregar a página interna `/home`, o script [home.js](file:///c:/Users/israe/Documents/ESTUDOS%20PROGRAMA%C3%87%C3%83O%20WEB/projeto-grau-tec/ello-mineiro-mvp/frontend/static/js/home.js) dispara uma validação ao backend (`GET /api/me`).
* Se o cookie de sessão estiver expirado ou ausente, o usuário é expulso imediatamente de volta para a tela de login.
* **Privacidade Visual:** No painel autenticado, os números de CPF e RG são mascarados com asteriscos centrais (ex: `123.***.***-01` e `MG-18.***-1`), impedindo que curiosos ao redor leiam os dados pessoais do aluno na tela.

---

## 5. Roteiro de Fala para a Apresentação (Pitch do Front-end)

> *"Na camada de Front-end, o nosso objetivo foi criar uma experiência acolhedora, profissional e extremamente rápida.  
> Adotamos a arquitetura Vanilla — sem frameworks inchados como React — o que torna a aplicação leve e imune a quebras de bibliotecas.  
> A identidade visual em azul marinho e dourado transmite a seriedade que uma instituição de ensino exige, usando ícones vetoriais modernos do Bootstrap Icons.  
> Mas o grande diferencial está nos detalhes de usabilidade: o formulário conta com integração em tempo real com o ViaCEP dos Correios para autopreenchimento de endereço, máscaras inteligentes que se adaptam a telefones celulares e fixos, e cálculo matemático do CPF na digitação.  
> Além disso, no painel do aluno, aplicamos o mascaramento de dados sensíveis para proteger a privacidade física na tela. É uma interface feita para acolher o usuário e evitar que ele cometa erros de digitação."*
