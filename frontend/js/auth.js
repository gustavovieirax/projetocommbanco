// ============================================================
// js/auth.js — Funções compartilhadas de autenticação
// Descrição: Protege as páginas do painel e envia o token à API.
// ============================================================

const API = 'http://127.0.0.1:8000';

// Bloqueia a página quando não existe uma sessão salva.
function protegerPagina() {
  if (!localStorage.getItem('token')) {
    window.location.replace('login.html');
  }
}

// Envia uma requisição autenticada à API.
async function fetchAutenticado(url, opcoes = {}) {
  const token = localStorage.getItem('token');
  if (!token) {
    protegerPagina();
    throw new Error('Faça login para continuar.');
  }

  const resposta = await fetch(url, {
    ...opcoes,
    headers: {
      ...opcoes.headers,
      Authorization: `Bearer ${token}`
    }
  });

  if (resposta.status === 401) {
    sair();
  }

  return resposta;
}

// Apaga os dados da sessão e volta para a tela de login.
function sair() {
  localStorage.removeItem('token');
  localStorage.removeItem('usuario');
  window.location.replace('login.html');
}

// Exibe uma mensagem de retorno usando o estilo de alerta do Bootstrap.
function exibirMensagem(id, texto, tipo = 'danger') {
  const elemento = document.getElementById(id);
  if (!elemento) {
    return;
  }

  elemento.className = `alert alert-${tipo} mt-3 mb-0`;
  elemento.textContent = texto;
}

// Converte texto de dados em texto HTML seguro para tabelas.
function escaparHtml(valor) {
  return String(valor ?? '').replace(/[&<>"']/g, (caractere) => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  })[caractere]);
}

// Retorna o detalhe do erro enviado pela API.
async function detalheErro(resposta, mensagemPadrao) {
  const erro = await resposta.json();
  return erro.detail || mensagemPadrao;
}
