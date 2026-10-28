// ============================================================
// js/login.js — Login e armazenamento do token
// ============================================================

const API = 'http://127.0.0.1:8000';
const formLogin = document.getElementById('form-login');

// Autentica o usuário e envia para o dashboard.
formLogin.addEventListener('submit', async (evento) => {
  evento.preventDefault();
  const dados = {
    email: document.getElementById('email').value.trim(),
    senha: document.getElementById('senha').value
  };

  try {
    const resposta = await fetch(`${API}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(dados)
    });
    const resultado = await resposta.json();
    if (!resposta.ok) {
      throw new Error(resultado.detail || resultado.erro || 'Não foi possível entrar.');
    }

    const token = resultado.access_token || resultado.acess_token;
    if (!token) {
      throw new Error('A resposta da API não trouxe um token de acesso.');
    }

    localStorage.setItem('token', token);
    localStorage.setItem('usuario', JSON.stringify(resultado.usuario));
    window.location.href = 'dashboard.html';
  } catch (erro) {
    const mensagem = document.getElementById('mensagemLogin');
    mensagem.className = 'alert alert-danger mt-3 mb-0';
    mensagem.textContent = `Erro ao entrar: ${erro.message}`;
  }
});
