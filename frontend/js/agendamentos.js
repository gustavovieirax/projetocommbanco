// ============================================================
// js/agendamentos.js — Cadastro e listagem de agendamentos
// ============================================================

protegerPagina();

const formAgendamento = document.getElementById('form-agendamento');

// Carrega os clientes e tatuadores disponíveis nos campos de seleção.
async function carregarOpcoesAgendamento() {
  const [respostaClientes, respostaTatuadores] = await Promise.all([
    fetchAutenticado(`${API}/clientes`),
    fetchAutenticado(`${API}/tatuadores`)
  ]);
  if (!respostaClientes.ok) {
    throw new Error(await detalheErro(respostaClientes, 'Não foi possível carregar os clientes.'));
  }
  if (!respostaTatuadores.ok) {
    throw new Error(await detalheErro(respostaTatuadores, 'Não foi possível carregar os tatuadores.'));
  }

  const [clientes, tatuadores] = await Promise.all([
    respostaClientes.json(),
    respostaTatuadores.json()
  ]);

  document.getElementById('idcliente').innerHTML = '<option value="">Cliente...</option>' + clientes.map((item) => `
    <option value="${escaparHtml(item.idcliente)}">${escaparHtml(item.nome)}</option>
  `).join('');
  document.getElementById('idtatuador').innerHTML = '<option value="">Tatuador...</option>' + tatuadores.map((item) => `
    <option value="${escaparHtml(item.idtatuador)}">${escaparHtml(item.nometatuador)}</option>
  `).join('');
}

// Carrega os agendamentos existentes.
async function carregarAgendamentos() {
  try {
    const resposta = await fetchAutenticado(`${API}/agendamentos`);
    if (!resposta.ok) {
      throw new Error(await detalheErro(resposta, 'Não foi possível carregar os agendamentos.'));
    }

    const agendamentos = await resposta.json();
    document.getElementById('corpo-tabela').innerHTML = agendamentos.map((item) => `
      <tr>
        <td>${escaparHtml(item.idagendamento)}</td>
        <td>${escaparHtml(item.nome_cliente || '-')}</td>
        <td>${escaparHtml(item.nometatuador || '-')}</td>
        <td>${escaparHtml(item.dataagendamento)}</td>
        <td>${escaparHtml(item.horaagendamento)}</td>
        <td>${item.valortatuagem == null ? '-' : escaparHtml(Number(item.valortatuagem).toFixed(2))}</td>
        <td>${escaparHtml(item.status)}</td>
      </tr>
    `).join('');
  } catch (erro) {
    exibirMensagem('mensagemAgendamentos', `Erro ao carregar agendamentos: ${erro.message}`);
  }
}

// Cadastra um agendamento e atualiza a tabela.
formAgendamento.addEventListener('submit', async (evento) => {
  evento.preventDefault();
  const valor = document.getElementById('valortatuagem').value;
  const agendamento = {
    idcliente: Number(document.getElementById('idcliente').value),
    idtatuador: Number(document.getElementById('idtatuador').value),
    dataagendamento: document.getElementById('dataagendamento').value,
    horaagendamento: document.getElementById('horaagendamento').value,
    descricaotatuagem: document.getElementById('descricaotatuagem').value.trim() || null,
    valortatuagem: valor === '' ? null : Number(valor),
    status: document.getElementById('status').value
  };

  try {
    const resposta = await fetchAutenticado(`${API}/agendamentos`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(agendamento)
    });
    if (!resposta.ok) {
      throw new Error(await detalheErro(resposta, 'Não foi possível cadastrar o agendamento.'));
    }

    formAgendamento.reset();
    exibirMensagem('mensagemAgendamentos', 'Agendamento cadastrado com sucesso.', 'success');
    await carregarAgendamentos();
  } catch (erro) {
    exibirMensagem('mensagemAgendamentos', `Erro ao cadastrar agendamento: ${erro.message}`);
  }
});

async function iniciarPagina() {
  try {
    await carregarOpcoesAgendamento();
    await carregarAgendamentos();
  } catch (erro) {
    exibirMensagem('mensagemAgendamentos', `Erro ao preparar a página: ${erro.message}`);
  }
}

iniciarPagina();
