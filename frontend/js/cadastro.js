// ============================================================
// js/cadastro.js — Cadastro de funcionários
// ============================================================

protegerPagina();

const formCadastro = document.getElementById('form-cadastro');

// Envia o cadastro autenticado para a rota disponível na API atual.
formCadastro.addEventListener('submit', async (evento) => {
  evento.preventDefault();
  const usuario = {
    nome: document.getElementById('nome').value.trim(),
    email: document.getElementById('email').value.trim(),
    senha: document.getElementById('senha').value
  };

  try {
    const resposta = await fetchAutenticado(`${API}/usuarios/cadastro`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(usuario)
    });
    if (!resposta.ok) {
      throw new Error(await detalheErro(resposta, 'Não foi possível cadastrar o funcionário.'));
    }

    formCadastro.reset();
    exibirMensagem('mensagemCadastro', 'Funcionário cadastrado com sucesso.', 'success');
  } catch (erro) {
    exibirMensagem('mensagemCadastro', `Erro ao cadastrar funcionário: ${erro.message}`);
  }
});
