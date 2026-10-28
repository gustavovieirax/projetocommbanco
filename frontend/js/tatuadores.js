// ============================================================
// js/tatuadores.js — Cadastro e listagem de tatuadores
// ============================================================

protegerPagina();

const formTatuador = document.getElementById('form-tatuador');

// Carrega as opções de senioridade para o formulário.
async function carregarOpcoesSenioridade() {
  const resposta = await fetchAutenticado(`${API}/senioridades`);
  if (!resposta.ok) {
    throw new Error(await detalheErro(resposta, 'Não foi possível carregar as senioridades.'));
  }

  const senioridades = await resposta.json();
  const select = document.getElementById('idsenioridade');
  select.innerHTML = '<option value="">Senioridade...</option>' + senioridades.map((item) => `
    <option value="${escaparHtml(item.idsenioridade)}">${escaparHtml(item.nome)}</option>
  `).join('');
}

// Carrega os tatuadores cadastrados na API.
async function carregarTatuadores() {
  try {
    const resposta = await fetchAutenticado(`${API}/tatuadores`);
    if (!resposta.ok) {
      throw new Error(await detalheErro(resposta, 'Não foi possível carregar os tatuadores.'));
    }

    const tatuadores = await resposta.json();
    document.getElementById('corpo-tabela').innerHTML = tatuadores.map((item) => `
      <tr>
        <td>${escaparHtml(item.idtatuador)}</td>
        <td>${escaparHtml(item.nometatuador)}</td>
        <td>${escaparHtml(item.cpf)}</td>
        <td>${escaparHtml(item.email || '-')}</td>
        <td>${escaparHtml(item.telefone || '-')}</td>
        <td>${escaparHtml(item.senioridade || '-')}</td>
      </tr>
    `).join('');
  } catch (erro) {
    exibirMensagem('mensagemTatuadores', `Erro ao carregar tatuadores: ${erro.message}`);
  }
}

// Cadastra um tatuador e atualiza a tabela.
formTatuador.addEventListener('submit', async (evento) => {
  evento.preventDefault();
  const tatuador = {
    nometatuador: document.getElementById('nometatuador').value.trim(),
    cpf: document.getElementById('cpf').value.trim(),
    email: document.getElementById('email').value.trim() || null,
    telefone: document.getElementById('telefone').value.trim() || null,
    datacontratacao: document.getElementById('datacontratacao').value || null,
    idsenioridade: Number(document.getElementById('idsenioridade').value)
  };

  try {
    const resposta = await fetchAutenticado(`${API}/tatuadores`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(tatuador)
    });
    if (!resposta.ok) {
      throw new Error(await detalheErro(resposta, 'Não foi possível cadastrar o tatuador.'));
    }

    formTatuador.reset();
    exibirMensagem('mensagemTatuadores', 'Tatuador cadastrado com sucesso.', 'success');
    await carregarTatuadores();
  } catch (erro) {
    exibirMensagem('mensagemTatuadores', `Erro ao cadastrar tatuador: ${erro.message}`);
  }
});

async function iniciarPagina() {
  try {
    await carregarOpcoesSenioridade();
    await carregarTatuadores();
  } catch (erro) {
    exibirMensagem('mensagemTatuadores', `Erro ao preparar a página: ${erro.message}`);
  }
}

iniciarPagina();
