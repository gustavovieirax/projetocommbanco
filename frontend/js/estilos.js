// ============================================================
// js/estilos.js — Cadastro e listagem de estilos
// ============================================================

protegerPagina();

const formEstilo = document.getElementById('form-estilo');

// Carrega os estilos cadastrados na API.
async function carregarEstilos() {
  try {
    const resposta = await fetchAutenticado(`${API}/estilos`);
    if (!resposta.ok) {
      throw new Error(await detalheErro(resposta, 'Não foi possível carregar os estilos.'));
    }

    const estilos = await resposta.json();
    document.getElementById('corpo-tabela').innerHTML = estilos.map((item) => `
      <tr>
        <td>${escaparHtml(item.idestilo)}</td>
        <td>${escaparHtml(item.descricao)}</td>
      </tr>
    `).join('');
  } catch (erro) {
    exibirMensagem('mensagemEstilos', `Erro ao carregar estilos: ${erro.message}`);
  }
}

// Cadastra um estilo e atualiza a tabela.
formEstilo.addEventListener('submit', async (evento) => {
  evento.preventDefault();
  const descricao = document.getElementById('descricao').value.trim();

  try {
    const resposta = await fetchAutenticado(`${API}/estilos`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ descricao })
    });
    if (!resposta.ok) {
      throw new Error(await detalheErro(resposta, 'Não foi possível cadastrar o estilo.'));
    }

    formEstilo.reset();
    exibirMensagem('mensagemEstilos', 'Estilo cadastrado com sucesso.', 'success');
    await carregarEstilos();
  } catch (erro) {
    exibirMensagem('mensagemEstilos', `Erro ao cadastrar estilo: ${erro.message}`);
  }
});

carregarEstilos();
