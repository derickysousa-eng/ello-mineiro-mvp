/**
 * =====================================================================
 * Escola Particular Ello Mineiro — Script do Painel Institucional (home.js)
 * Gerencia a guarda de rotas (Route Guard), mascaramento de dados sensíveis (CPF e RG),
 * visibilidade condicional de menus e controle de permissões de acesso.
 * =====================================================================
 */

document.addEventListener("DOMContentLoaded", () => {
  carregarDadosUsuario();
  initLogout();
  initModalPermissaoOutsideClick();
});

/**
 * Formata data no padrão brasileiro DD/MM/AAAA
 */
function formatarDataBR(dataIso) {
  if (!dataIso) return "Não informada";
  const [ano, mes, dia] = dataIso.split("-");
  if (!ano || !mes || !dia) return dataIso;
  return `${dia}/${mes}/${ano}`;
}

/**
 * Formata CPF com proteção visual de privacidade (ex: 123.***.***-01)
 */
function formatarCpfPrivacidade(cpf) {
  if (!cpf) return "Não informado";
  const limpo = cpf.replace(/\D/g, "");
  if (limpo.length !== 11) return "***.***.***-**";
  return `${limpo.slice(0, 3)}.***.***-${limpo.slice(9, 11)}`;
}

/**
 * Formata RG com proteção visual de privacidade (ex: 12.***-9 ou MG-78.***-1),
 * preservando a sigla do estado caso exista e ocultando os dígitos centrais.
 */
function formatarRgPrivacidade(rg) {
  if (!rg) return "Não informado";
  const str = rg.toString().trim().toUpperCase();

  // Detecta se começa com sigla de estado (ex: MG, SP, RJ, etc.)
  const matchUf = str.match(/^([A-Z]{2})[\s\-.]*(.*)$/);
  let prefixoUf = "";
  let corpo = str;

  if (matchUf) {
    prefixoUf = `${matchUf[1]}-`;
    corpo = matchUf[2];
  }

  // Extrai apenas dígitos numéricos e a letra X
  const clean = corpo.replace(/[^0-9X]/g, "");
  if (!clean) return str;

  if (clean.length <= 4) {
    return `${prefixoUf}**.***`;
  }

  const inicio = clean.slice(0, 2);
  const fim = clean.slice(-1);
  return `${prefixoUf}${inicio}.***-${fim}`;
}


/**
 * Formata telefone brasileiro para exibição
 */
function formatarTelefoneVisual(tel) {
  if (!tel) return "Não informado";
  const digits = tel.replace(/\D/g, "");
  if (digits.length === 10) {
    return `(${digits.slice(0, 2)}) ${digits.slice(2, 6)}-${digits.slice(6)}`;
  }
  if (digits.length === 11) {
    return `(${digits.slice(0, 2)}) ${digits.slice(2, 7)}-${digits.slice(7)}`;
  }
  return tel;
}

/**
 * Formata CEP no formato 00000-000
 */
function formatarCepVisual(cep) {
  if (!cep) return "—";
  const digits = cep.replace(/\D/g, "");
  if (digits.length === 8) {
    return `${digits.slice(0, 5)}-${digits.slice(5)}`;
  }
  return cep;
}

/**
 * Executa a guarda de rota chamando GET /api/me.
 * Se autenticado, preenche os elementos da tela; caso contrário, redireciona para o login.
 */
async function carregarDadosUsuario() {
  try {
    const response = await fetch("/api/me", {
      method: "GET",
      headers: { "Accept": "application/json" }
    });

    if (response.status === 401 || !response.ok) {
      // Sessão ausente ou expirada: redireciona para a tela de login
      window.location.href = "/";
      return;
    }

    const usuario = await response.json();
    preencherDashboard(usuario);
  } catch (err) {
    console.error("Erro ao validar sessão:", err);
    window.location.href = "/";
  }
}

/**
 * Preenche a interface com os dados do usuário autenticado e ajusta menus contextuais.
 */
function preencherDashboard(u) {
  // Cabeçalho e Saudação
  const elSaudacao = document.getElementById("usuario-saudacao");
  if (elSaudacao) {
    const primeiroNome = u.nome ? u.nome.split(" ")[0] : "Usuário";
    elSaudacao.textContent = `Olá, ${primeiroNome}!`;
  }

  const elBadge = document.getElementById("usuario-perfil-badge");
  if (elBadge) {
    elBadge.textContent = u.permissao_nome || "Usuário";
  }

  // Ocultação/Exibição condicional do menu Notas (apenas para 'Professor' ou 'Aluno')
  const menuNotas = document.getElementById("menu-notas");
  if (menuNotas) {
    const perm = (u.permissao_nome || "").toLowerCase();
    if (perm === "professor" || perm === "aluno") {
      menuNotas.style.display = "block";
    } else {
      menuNotas.style.display = "none";
    }
  }

  // Card 1: Perfil do Usuário com Proteção de Dados Pessoais (CPF e RG)
  document.getElementById("perfil-nome").textContent = u.nome || "—";
  document.getElementById("perfil-login").textContent = `@${u.user_login}`;
  document.getElementById("perfil-email").textContent = u.email || "—";
  document.getElementById("perfil-genero").textContent = u.genero || "Não informado";
  document.getElementById("perfil-nasc").textContent = formatarDataBR(u.data_nasc);
  document.getElementById("perfil-cpf").textContent = formatarCpfPrivacidade(u.cpf);
  document.getElementById("perfil-rg").textContent = formatarRgPrivacidade(u.rg);
  document.getElementById("perfil-telefone").textContent = formatarTelefoneVisual(u.telefone);
  document.getElementById("perfil-telefone-sec").textContent = formatarTelefoneVisual(u.telefone_sec);
  document.getElementById("perfil-status").textContent = u.ativo ? "Conta Ativa" : "Inativo";

  // Card 2: Endereço Residencial Ativo
  if (u.enderecos && u.enderecos.length > 0) {
    const end = u.enderecos[0];
    document.getElementById("endereco-tipo").textContent = end.tipo || "Residencial";
    document.getElementById("endereco-rua").textContent = end.rua || "—";
    document.getElementById("endereco-numero").textContent = end.numero || "—";
    document.getElementById("endereco-complemento").textContent = end.complemento || "Não possui";
    document.getElementById("endereco-bairro").textContent = end.bairro || "—";
    document.getElementById("endereco-cidade-uf").textContent = `${end.cidade || "—"} / ${end.uf || "—"}`;
    document.getElementById("endereco-cep").textContent = formatarCepVisual(end.cep);
    document.getElementById("endereco-situacao").textContent = end.situacao || "ATIVO";
  } else {
    document.getElementById("endereco-rua").textContent = "Nenhum endereço cadastrado";
  }
}

/**
 * Controle de Abertura e Fechamento do Modal de Permissões
 */
window.abrirAvisoPermissao = function () {
  const modal = document.getElementById("modal-permissoes");
  if (modal) modal.style.display = "flex";
};

window.fecharAvisoPermissao = function () {
  const modal = document.getElementById("modal-permissoes");
  if (modal) modal.style.display = "none";
};

function initModalPermissaoOutsideClick() {
  const modal = document.getElementById("modal-permissoes");
  if (modal) {
    modal.addEventListener("click", (e) => {
      if (e.target === modal) {
        modal.style.display = "none";
      }
    });
  }
}

/**
 * Inicializa ação de logout encerrando a sessão HttpOnly.
 */
function initLogout() {
  const btnLogout = document.getElementById("btn-logout");
  if (!btnLogout) return;

  btnLogout.addEventListener("click", async () => {
    if (confirm("Deseja realmente encerrar sua sessão no portal?")) {
      try {
        await fetch("/api/auth/logout", {
          method: "POST",
          headers: { "Content-Type": "application/json" }
        });
      } catch (err) {
        console.warn("Falha no logout via rede, redirecionando mesmo assim:", err);
      } finally {
        window.location.href = "/";
      }
    }
  });
}
