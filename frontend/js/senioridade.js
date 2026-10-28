// ============================================================
// js/senioridade.js — Cadastro e listagem de senioridades
// ============================================================

protegerPagina();

const formSenioridade = document.getElementById('form-senioridade');

// Carrega as senioridades cadastradas na API.
async function carregarSenioridades() {
  try {
    const resposta = await fetchAutenticado(`${API}/senioridades`);
    if (!resposta.ok) {
      throw new Error(await detalheErro(resposta, 'Não foi possível carregar as senioridades.'));
    }

    const senioridades = await resposta.json();
    document.getElementById('corpo-tabela').innerHTML = senioridades.map((item) => `
      <tr>
        <td>${escaparHtml(item.idsenioridade)}</td>
        <td>${escaparHtml(item.nome)}</td>
      </tr>
    `).join('');
  } catch (erro) {
    exibirMensagem('mensagemSenioridade', `Erro ao carregar senioridades: ${erro.message}`);
  }
}

// Cadastra uma senioridade e atualiza a tabela.
formSenioridade.addEventListener('submit', async (evento) => {
  evento.preventDefault();
  const nome = document.getElementById('nome').value.trim();

  try {
    const resposta = await fetchAutenticado(`${API}/senioridades`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ nome })
    });
    if (!resposta.ok) {
      throw new Error(await detalheErro(resposta, 'Não foi possível cadastrar a senioridade.'));
    }

    formSenioridade.reset();
    exibirMensagem('mensagemSenioridade', 'Senioridade cadastrada com sucesso.', 'success');
    await carregarSenioridades();
  } catch (erro) {
    exibirMensagem('mensagemSenioridade', `Erro ao cadastrar senioridade: ${erro.message}`);
  }
});

carregarSenioridades();
