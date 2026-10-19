/**
 * =====================================================================
 * Escola Particular Ello Mineiro — Script do Painel Acadêmico (home.js)
 * Implementa a guarda de rotas (Route Guard), carregamento dinâmico de perfil
 * e encerramento seguro de sessão (Logout).
 * =====================================================================
 */

document.addEventListener("DOMContentLoaded", () => {
  carregarDadosUsuario();
  initLogout();
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
 * Formata CPF com máscara e proteção de privacidade (ex: 123.***.***-01)
 */
function formatarCpfPrivacidade(cpf) {
  if (!cpf) return "Não informado";
  const limpo = cpf.replace(/\D/g, "");
  if (limpo.length !== 11) return cpf;
  return `${limpo.slice(0, 3)}.***.***-${limpo.slice(9, 11)}`;
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
 * Preenche a interface com os dados do usuário autenticado.
 */
function preencherDashboard(u) {
  // Cabeçalho e Saudação
  const elSaudacao = document.getElementById("usuario-saudacao");
  if (elSaudacao) {
    const primeiroNome = u.nome ? u.nome.split(" ")[0] : "Acadêmico";
    elSaudacao.textContent = `Olá, ${primeiroNome}!`;
  }

  const elBadge = document.getElementById("usuario-perfil-badge");
  if (elBadge) {
    elBadge.textContent = u.permissao_nome || "Aluno";
  }

  // Card 1: Perfil do Usuário
  document.getElementById("perfil-nome").textContent = u.nome || "—";
  document.getElementById("perfil-login").textContent = `@${u.user_login}`;
  document.getElementById("perfil-email").textContent = u.email || "—";
  document.getElementById("perfil-genero").textContent = u.genero || "Não informado";
  document.getElementById("perfil-nasc").textContent = formatarDataBR(u.data_nasc);
  document.getElementById("perfil-cpf").textContent = formatarCpfPrivacidade(u.cpf);
  document.getElementById("perfil-rg").textContent = u.rg || "Não informado";
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
