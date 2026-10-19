/**
 * =====================================================================
 * Escola Particular Ello Mineiro — Script de Autenticação (auth.js)
 * Gerencia login, cadastro, máscaras dinâmicas, validação módulo 11 de CPF,
 * Title Case com preposições em português, ViaCEP e tratamento de erros HTTP.
 * =====================================================================
 */

document.addEventListener("DOMContentLoaded", () => {
  initLogin();
  initCadastro();
  initPasswordToggles();
  initModalEsqueciSenha();
});

/* =====================================================================
   Utilitários de Formatação, Máscaras e Validação
===================================================================== */

/**
 * Capitaliza nomes próprios no padrão brasileiro (Title Case),
 * preservando preposições e conjunções em minúsculas (ex: "Carlos da Silva").
 */
function formatarTitleCase(texto) {
  if (!texto) return "";
  const preposicoes = new Set(["de", "da", "do", "das", "dos", "e"]);
  const palavras = texto.trim().split(/\s+/);

  return palavras
    .map((palavra, index) => {
      const min = palavra.toLowerCase();
      if (index > 0 && preposicoes.has(min)) {
        return min;
      }
      return min.charAt(0).toUpperCase() + min.slice(1);
    })
    .join(" ");
}

/**
 * Validação dos dígitos verificadores de CPF pelo algoritmo oficial (módulo 11).
 */
function validarCPF(cpfLimpo) {
  if (!cpfLimpo || cpfLimpo.length !== 11) return false;
  // Rejeita sequências conhecidas de dígitos repetidos
  if (/^(\d)\1{10}$/.test(cpfLimpo)) return false;

  let soma = 0;
  let resto;

  for (let i = 1; i <= 9; i++) {
    soma += parseInt(cpfLimpo.substring(i - 1, i), 10) * (11 - i);
  }
  resto = (soma * 10) % 11;
  if (resto === 10 || resto === 11) resto = 0;
  if (resto !== parseInt(cpfLimpo.substring(9, 10), 10)) return false;

  soma = 0;
  for (let i = 1; i <= 10; i++) {
    soma += parseInt(cpfLimpo.substring(i - 1, i), 10) * (12 - i);
  }
  resto = (soma * 10) % 11;
  if (resto === 10 || resto === 11) resto = 0;
  if (resto !== parseInt(cpfLimpo.substring(10, 11), 10)) return false;

  return true;
}

/**
 * Aplica máscara dinâmica de CPF: 000.000.000-00
 */
function mascaraCPF(valor) {
  const digits = valor.replace(/\D/g, "").slice(0, 11);
  if (digits.length <= 3) return digits;
  if (digits.length <= 6) return `${digits.slice(0, 3)}.${digits.slice(3)}`;
  if (digits.length <= 9) return `${digits.slice(0, 3)}.${digits.slice(3, 6)}.${digits.slice(6)}`;
  return `${digits.slice(0, 3)}.${digits.slice(3, 6)}.${digits.slice(6, 9)}-${digits.slice(9, 11)}`;
}

/**
 * Aplica máscara adaptativa de telefone (10 dígitos fixo vs 11 dígitos celular).
 */
function mascaraTelefone(valor) {
  const digits = valor.replace(/\D/g, "").slice(0, 11);
  if (digits.length <= 2) return digits ? `(${digits}` : "";
  if (digits.length <= 6) return `(${digits.slice(0, 2)}) ${digits.slice(2)}`;
  if (digits.length <= 10) {
    // Fixo: (XX) XXXX-XXXX
    return `(${digits.slice(0, 2)}) ${digits.slice(2, 6)}-${digits.slice(6)}`;
  }
  // Celular: (XX) 9XXXX-XXXX
  return `(${digits.slice(0, 2)}) ${digits.slice(2, 7)}-${digits.slice(7, 11)}`;
}

/**
 * Aplica máscara de CEP: 00000-000
 */
function mascaraCEP(valor) {
  const digits = valor.replace(/\D/g, "").slice(0, 8);
  if (digits.length <= 5) return digits;
  return `${digits.slice(0, 5)}-${digits.slice(5, 8)}`;
}

/**
 * Aplica máscara dinâmica de RG com Regex (de 7 até 13 dígitos, permitindo dígito verificador X).
 * Atende aos padrões estaduais (MG 8 dígitos, SP 9 dígitos e RN com até 13 caracteres).
 */
function mascaraRG(valor) {
  // Converte para maiúsculas e remove qualquer caractere que não seja número ou X
  let clean = valor.toUpperCase().replace(/[^0-9X]/g, "");
  
  // Se contiver X, só permite na última posição
  if (clean.indexOf("X") !== -1 && clean.indexOf("X") !== clean.length - 1) {
    clean = clean.replace(/X/g, "");
  }
  
  // Limitação máxima de 13 caracteres alfanuméricos úteis (teto de documentos como RN)
  clean = clean.slice(0, 13);
  const len = clean.length;
  
  if (len <= 2) return clean;
  if (len <= 5) return `${clean.slice(0, 2)}.${clean.slice(2)}`;
  if (len <= 8) return `${clean.slice(0, 2)}.${clean.slice(2, 5)}.${clean.slice(5)}`;
  if (len === 9) {
    // Padrão clássico: 00.000.000-X
    return `${clean.slice(0, 2)}.${clean.slice(2, 5)}.${clean.slice(5, 8)}-${clean.slice(8)}`;
  }
  if (len <= 11) {
    // Formato estendido (10 ou 11 dígitos): 00.000.000.00-X
    return `${clean.slice(0, 2)}.${clean.slice(2, 5)}.${clean.slice(5, 8)}.${clean.slice(8, len - 1)}-${clean.slice(len - 1)}`;
  }
  // Formato amplo até 13 dígitos (ex: RN): 00.000.000.000-X
  return `${clean.slice(0, 2)}.${clean.slice(2, 5)}.${clean.slice(5, 8)}.${clean.slice(8, len - 1)}-${clean.slice(len - 1)}`;
}


/**
 * Exibe mensagem de feedback visual em um campo.
 */
function setFieldFeedback(fieldId, isValid, message = "") {
  const input = document.getElementById(fieldId);
  const feedback = document.getElementById(`${fieldId}-feedback`);
  if (!input) return;

  if (isValid === true) {
    input.classList.remove("is-invalid");
    input.classList.add("is-valid");
    if (feedback) {
      feedback.textContent = message;
      feedback.className = "input-feedback show-valid";
    }
  } else if (isValid === false) {
    input.classList.remove("is-valid");
    input.classList.add("is-invalid");
    if (feedback) {
      feedback.textContent = message;
      feedback.className = "input-feedback show-error";
    }
  } else {
    input.classList.remove("is-valid", "is-invalid");
    if (feedback) {
      feedback.textContent = "";
      feedback.className = "input-feedback";
    }
  }
}

/**
 * Exibe alertas de formulário em container superior.
 */
function showAlert(containerId, type, message) {
  const alert = document.getElementById(containerId);
  if (!alert) return;
  alert.className = `alert alert-${type}`;
  alert.innerHTML = message;
  alert.style.display = "block";
  alert.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

function hideAlert(containerId) {
  const alert = document.getElementById(containerId);
  if (alert) alert.style.display = "none";
}

/* =====================================================================
   Fluxo da Tela de Login (frontend/index.html)
===================================================================== */
function initLogin() {
  const form = document.getElementById("login-form");
  if (!form) return;

  const btnLogin = document.getElementById("btn-login");
  const spinner = document.getElementById("login-spinner");
  const btnText = document.getElementById("btn-login-text");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideAlert("login-alert");

    const identificador = document.getElementById("identificador").value.trim();
    const senha = document.getElementById("senha").value;

    if (!identificador || !senha) {
      showAlert("login-alert", "error", "Por favor, preencha o identificador e a senha.");
      return;
    }

    // Estado de carregamento
    btnLogin.disabled = true;
    if (spinner) spinner.style.display = "inline-block";
    if (btnText) btnText.textContent = "Autenticando...";

    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ identificador, senha })
      });

      const data = await response.json().catch(() => ({}));

      if (response.ok) {
        showAlert("login-alert", "success", "Autenticação bem-sucedida! Redirecionando...");
        setTimeout(() => {
          window.location.href = "/home";
        }, 500);
      } else if (response.status === 401) {
        showAlert("login-alert", "error", "Identificador ou senha incorretos.");
      } else if (response.status === 429) {
        const retryAfter = response.headers.get("Retry-After") || 60;
        showAlert("login-alert", "warning", `Muitas tentativas de login consecutivas. Por segurança, aguarde ${retryAfter} segundos.`);
      } else {
        const msg = data.detail || "Erro inesperado ao realizar login. Tente novamente.";
        showAlert("login-alert", "error", msg);
      }
    } catch (err) {
      showAlert("login-alert", "error", "Não foi possível conectar ao servidor. Verifique sua conexão.");
    } finally {
      btnLogin.disabled = false;
      if (spinner) spinner.style.display = "none";
      if (btnText) btnText.textContent = "Entrar no Portal";
    }
  });
}

/* =====================================================================
   Fluxo da Tela de Cadastro (frontend/cadastro.html)
===================================================================== */
function initCadastro() {
  const form = document.getElementById("cadastro-form");
  if (!form) return;

  // 1. Title Case inteligente no nome completo (blur e submit)
  const inputNome = document.getElementById("nome");
  if (inputNome) {
    inputNome.addEventListener("blur", () => {
      const formatado = formatarTitleCase(inputNome.value);
      inputNome.value = formatado;
      if (formatado.length >= 2) {
        setFieldFeedback("nome", true);
      } else {
        setFieldFeedback("nome", false, "O nome deve conter pelo menos 2 caracteres.");
      }
    });
  }

  // 2. Máscara e validação em tempo real de CPF
  const inputCpf = document.getElementById("cpf");
  if (inputCpf) {
    inputCpf.addEventListener("input", (e) => {
      e.target.value = mascaraCPF(e.target.value);
      const limpo = e.target.value.replace(/\D/g, "");
      if (limpo.length === 11) {
        if (validarCPF(limpo)) {
          setFieldFeedback("cpf", true, "CPF válido.");
        } else {
          setFieldFeedback("cpf", false, "CPF inválido.");
        }
      } else {
        setFieldFeedback("cpf", null);
      }
    });
  }

  // 2.1. Máscara e validação em tempo real de RG (Regex com suporte de 7 a 13 dígitos)
  const inputRg = document.getElementById("rg");
  if (inputRg) {
    inputRg.addEventListener("input", (e) => {
      e.target.value = mascaraRG(e.target.value);
      const cleanRg = e.target.value.toUpperCase().replace(/[^0-9X]/g, "");
      if (cleanRg.length >= 7 && cleanRg.length <= 13) {
        setFieldFeedback("rg", true, "RG no formato válido.");
      } else if (cleanRg.length > 0) {
        setFieldFeedback("rg", false, "O RG deve conter entre 7 e 13 dígitos.");
      } else {
        setFieldFeedback("rg", null);
      }
    });
  }


  // 3. Máscaras adaptativas de Telefone
  ["telefone", "telefone_sec"].forEach((id) => {
    const inputTel = document.getElementById(id);
    if (!inputTel) return;

    inputTel.addEventListener("input", (e) => {
      e.target.value = mascaraTelefone(e.target.value);
      const digits = e.target.value.replace(/\D/g, "");
      if (digits.length >= 10) {
        setFieldFeedback(id, true);
      } else if (id === "telefone" && digits.length > 0) {
        setFieldFeedback(id, false, "Telefone incompleto.");
      } else {
        setFieldFeedback(id, null);
      }
    });
  });

  // 4. Medidor de força de senha e validação de requisitos
  const inputSenha = document.getElementById("senha");
  const inputConfirmaSenha = document.getElementById("confirma_senha");
  const meterBar = document.getElementById("password-meter-bar");
  const meter = document.getElementById("password-meter");

  if (inputSenha) {
    inputSenha.addEventListener("input", () => {
      const val = inputSenha.value;
      if (!val) {
        if (meter) meter.style.display = "none";
        setFieldFeedback("senha", null);
        return;
      }

      if (meter) meter.style.display = "block";
      let score = 0;
      if (val.length >= 8) score += 25;
      if (/[A-Z]/.test(val)) score += 25;
      if (/[0-9]/.test(val)) score += 25;
      if (/[^A-Za-z0-9]/.test(val)) score += 25;

      meterBar.style.width = `${score}%`;
      if (score <= 25) {
        meterBar.style.backgroundColor = "var(--color-error)";
        setFieldFeedback("senha", false, "Senha fraca (mínimo 8 caracteres).");
      } else if (score <= 50) {
        meterBar.style.backgroundColor = "var(--color-warning)";
        setFieldFeedback("senha", true, "Senha moderada.");
      } else {
        meterBar.style.backgroundColor = "var(--color-success)";
        setFieldFeedback("senha", true, "Senha forte.");
      }

      if (inputConfirmaSenha && inputConfirmaSenha.value) {
        validarCoincidenciaSenha();
      }
    });
  }

  function validarCoincidenciaSenha() {
    if (!inputConfirmaSenha) return true;
    if (inputSenha.value !== inputConfirmaSenha.value) {
      setFieldFeedback("confirma_senha", false, "As senhas não coincidem.");
      return false;
    }
    setFieldFeedback("confirma_senha", true, "Senhas coincidem.");
    return true;
  }

  if (inputConfirmaSenha) {
    inputConfirmaSenha.addEventListener("input", validarCoincidenciaSenha);
  }

  // 5. Integração com ViaCEP
  const inputCep = document.getElementById("cep");
  if (inputCep) {
    inputCep.addEventListener("input", async (e) => {
      e.target.value = mascaraCEP(e.target.value);
      const cleanCep = e.target.value.replace(/\D/g, "");

      if (cleanCep.length === 8) {
        setFieldFeedback("cep", null, "Buscando endereço...");
        try {
          const res = await fetch(`https://viacep.com.br/ws/${cleanCep}/json/`);
          const data = await res.json();

          if (data.erro) {
            setFieldFeedback("cep", false, "CEP não encontrado. Preencha manualmente.");
            liberarEdicaoEndereco();
          } else {
            setFieldFeedback("cep", true, "Endereço localizado com sucesso!");
            if (data.logradouro) document.getElementById("rua").value = data.logradouro;
            if (data.bairro) document.getElementById("bairro").value = data.bairro;
            if (data.localidade) document.getElementById("cidade").value = data.localidade;
            if (data.uf) document.getElementById("uf").value = data.uf.toUpperCase();

            // Foco imediato no número para agilizar preenchimento
            const numInput = document.getElementById("numero");
            if (numInput) numInput.focus();
          }
        } catch (err) {
          setFieldFeedback("cep", false, "Serviço ViaCEP indisponível. Preencha manualmente.");
          liberarEdicaoEndereco();
        }
      } else {
        setFieldFeedback("cep", null);
      }
    });
  }

  function liberarEdicaoEndereco() {
    ["rua", "bairro", "cidade", "uf"].forEach((id) => {
      const el = document.getElementById(id);
      if (el) el.readOnly = false;
    });
  }

  // 6. Submissão do Formulário de Cadastro
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideAlert("cadastro-alert");

    // Validações prévias
    const userLogin = document.getElementById("user_login").value.trim();
    const email = document.getElementById("email").value.trim();
    const senha = document.getElementById("senha").value;
    const confirmaSenha = document.getElementById("confirma_senha").value;
    const nome = formatarTitleCase(document.getElementById("nome").value);
    document.getElementById("nome").value = nome;

    const genero = document.getElementById("genero").value;
    const dataNasc = document.getElementById("data_nasc").value;
    const cpfLimpo = document.getElementById("cpf").value.replace(/\D/g, "");
    const rg = document.getElementById("rg").value.trim();
    const telefoneLimpo = document.getElementById("telefone").value.replace(/\D/g, "");
    const telefoneSecLimpo = document.getElementById("telefone_sec").value.replace(/\D/g, "") || null;

    const cepLimpo = document.getElementById("cep").value.replace(/\D/g, "");
    const rua = document.getElementById("rua").value.trim();
    const numero = document.getElementById("numero").value.trim();
    const complemento = document.getElementById("complemento").value.trim() || null;
    const bairro = document.getElementById("bairro").value.trim();
    const cidade = document.getElementById("cidade").value.trim();
    const uf = document.getElementById("uf").value;
    const aceiteTermos = document.getElementById("aceite_termos").checked;

    if (!aceiteTermos) {
      showAlert("cadastro-alert", "error", "Você precisa aceitar os Termos e Condições para se cadastrar.");
      return;
    }

    if (senha.length < 8) {
      showAlert("cadastro-alert", "error", "A senha deve conter no mínimo 8 caracteres.");
      return;
    }

    if (senha !== confirmaSenha) {
      showAlert("cadastro-alert", "error", "As senhas informadas não conferem.");
      return;
    }

    if (!validarCPF(cpfLimpo)) {
      showAlert("cadastro-alert", "error", "O CPF informado é inválido. Verifique os números digitados.");
      return;
    }

    if (cepLimpo.length !== 8) {
      showAlert("cadastro-alert", "error", "O CEP deve conter 8 dígitos.");
      return;
    }

    if (!rua || !numero || !bairro || !cidade || !uf) {
      showAlert("cadastro-alert", "error", "Preencha todos os campos obrigatórios do endereço residencial.");
      return;
    }

    // Montagem do payload higienizado para o backend
    const payload = {
      user_login: userLogin,
      email: email,
      senha: senha,
      nome: nome,
      genero: genero,
      cpf: cpfLimpo,
      rg: rg,
      data_nasc: dataNasc,
      telefone: telefoneLimpo,
      telefone_sec: telefoneSecLimpo,
      endereco: {
        tipo: "Residencial",
        cep: cepLimpo,
        rua: rua,
        numero: numero,
        bairro: bairro,
        complemento: complemento,
        cidade: cidade,
        uf: uf
      }
    };

    const btnCadastrar = document.getElementById("btn-cadastrar");
    const spinner = document.getElementById("cadastro-spinner");
    const btnText = document.getElementById("btn-cadastrar-text");

    btnCadastrar.disabled = true;
    if (spinner) spinner.style.display = "inline-block";
    if (btnText) btnText.textContent = "Processando Cadastro...";

    try {
      const response = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await response.json().catch(() => ({}));

      if (response.status === 201) {
        showAlert(
          "cadastro-alert",
          "success",
          "Cadastro realizado com sucesso! Redirecionando para a tela de login..."
        );
        setTimeout(() => {
          window.location.href = "/";
        }, 1500);
      } else if (response.status === 409) {
        showAlert("cadastro-alert", "error", data.detail || "Nome de usuário ou e-mail já cadastrado.");
      } else if (response.status === 422) {
        let msg = "Dados inválidos: ";
        if (Array.isArray(data.detail)) {
          msg += data.detail.map((e) => e.msg).join(", ");
        } else {
          msg += data.detail || "Verifique os dados preenchidos.";
        }
        showAlert("cadastro-alert", "error", msg);
      } else if (response.status === 429) {
        showAlert("cadastro-alert", "warning", "Muitas tentativas de cadastro. Por favor, aguarde alguns minutos.");
      } else {
        showAlert("cadastro-alert", "error", data.detail || "Erro inesperado ao cadastrar. Tente novamente.");
      }
    } catch (err) {
      showAlert("cadastro-alert", "error", "Falha de comunicação com o servidor. Tente novamente mais tarde.");
    } finally {
      btnCadastrar.disabled = false;
      if (spinner) spinner.style.display = "none";
      if (btnText) btnText.textContent = "Concluir Cadastro";
    }
  });
}

/* =====================================================================
   Botões de Alternância de Visibilidade de Senha (Bootstrap Icons)
===================================================================== */
function initPasswordToggles() {
  const toggles = [
    { btnId: "btn-toggle-senha", inputId: "senha" },
    { btnId: "btn-toggle-senha-cad", inputId: "senha" }
  ];

  toggles.forEach(({ btnId, inputId }) => {
    const btn = document.getElementById(btnId);
    const input = document.getElementById(inputId);
    if (btn && input) {
      btn.addEventListener("click", () => {
        const isPassword = input.type === "password";
        input.type = isPassword ? "text" : "password";
        const icon = btn.querySelector("i");
        if (icon) {
          icon.className = isPassword ? "bi bi-eye-slash" : "bi bi-eye";
        }
      });
    }
  });
}

/* =====================================================================
   Modal Informativo: Esqueci Minha Senha
===================================================================== */
function initModalEsqueciSenha() {
  const linkModal = document.getElementById("link-esqueci-senha");
  const modal = document.getElementById("modal-esqueci-senha");
  const btnFechar = document.getElementById("btn-fechar-modal");

  if (linkModal && modal) {
    linkModal.addEventListener("click", (e) => {
      e.preventDefault();
      modal.style.display = "flex";
    });
  }

  if (btnFechar && modal) {
    btnFechar.addEventListener("click", () => {
      modal.style.display = "none";
    });
  }

  if (modal) {
    modal.addEventListener("click", (e) => {
      if (e.target === modal) {
        modal.style.display = "none";
      }
    });
  }
}
