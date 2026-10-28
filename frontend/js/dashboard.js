// ============================================================
// js/dashboard.js — Carrega a sessão do painel
// ============================================================

protegerPagina();

// Valida a sessão com a API e mostra os dados do usuário.
async function carregarDashboard() {
  try {
    const resposta = await fetchAutenticado(`${API}/dashboard`);
    if (!resposta.ok) {
      throw new Error(await detalheErro(resposta, 'A sessão não é válida.'));
    }

    const dados = await resposta.json();
    const usuario = document.getElementById('usuario');
    usuario.textContent = `Bem-vindo(a), ${dados.usuario.nome} — ${dados.usuario.email}`;
  } catch (erro) {
    exibirMensagem('mensagemDashboard', `Não foi possível carregar o painel: ${erro.message}`);
  }
}

carregarDashboard();
