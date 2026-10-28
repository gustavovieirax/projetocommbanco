// ============================================================
// js/clientes.js — Cadastro e listagem de clientes
// ============================================================

protegerPagina();

const formCliente = document.getElementById('form-cliente');

// Carrega os clientes cadastrados na API.
async function carregarClientes() {
  try {
    const resposta = await fetchAutenticado(`${API}/clientes`);
    if (!resposta.ok) {
      throw new Error(await detalheErro(resposta, 'Não foi possível carregar os clientes.'));
    }

    const clientes = await resposta.json();
    const corpoTabela = document.getElementById('corpo-tabela');
    corpoTabela.innerHTML = clientes.map((cliente) => `
      <tr>
        <td>${escaparHtml(cliente.idcliente)}</td>
        <td>${escaparHtml(cliente.nome)}</td>
        <td>${escaparHtml(cliente.cpf)}</td>
        <td>${escaparHtml(cliente.telefone || '-')}</td>
        <td>${escaparHtml(cliente.cidade || '-')}</td>
        <td>${escaparHtml(cliente.uf || '-')}</td>
      </tr>
    `).join('');
  } catch (erro) {
    exibirMensagem('mensagemClientes', `Erro ao carregar clientes: ${erro.message}`);
  }
}

// Cadastra um cliente e atualiza a tabela.
formCliente.addEventListener('submit', async (evento) => {
  evento.preventDefault();
  const cliente = {
    nome: document.getElementById('nome').value.trim(),
    cpf: document.getElementById('cpf').value.trim(),
    telefone: document.getElementById('telefone').value.trim() || null,
    datacadastro: document.getElementById('datacadastro').value || null,
    cidade: document.getElementById('cidade').value.trim() || null,
    uf: document.getElementById('uf').value.trim().toUpperCase() || null
  };

  try {
    const resposta = await fetchAutenticado(`${API}/clientes`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(cliente)
    });
    if (!resposta.ok) {
      throw new Error(await detalheErro(resposta, 'Não foi possível cadastrar o cliente.'));
    }

    formCliente.reset();
    exibirMensagem('mensagemClientes', 'Cliente cadastrado com sucesso.', 'success');
    await carregarClientes();
  } catch (erro) {
    exibirMensagem('mensagemClientes', `Erro ao cadastrar cliente: ${erro.message}`);
  }
});

carregarClientes();
