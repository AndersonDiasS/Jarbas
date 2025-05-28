const fs = require('fs');
const path = require('path');

const MEMORIA_PATH = path.resolve('historicos/memoria.json');

let memoria = [];

function carregarMemoria() {
  if (fs.existsSync(MEMORIA_PATH)) {
    const dados = fs.readFileSync(MEMORIA_PATH, 'utf8');
    try {
      memoria = JSON.parse(dados);
    } catch (e) {
      console.error('❌ Erro ao carregar memória:', e.message);
      memoria = [];
    }
  }
}

function salvarMemoria() {
  fs.writeFileSync(MEMORIA_PATH, JSON.stringify(memoria, null, 2));
}

function lembrar(pergunta, resposta) {
  memoria.push({ tipo: 'mensagem', pergunta, resposta });
  salvarMemoria();
}

function limparMemoria() {
  memoria = [];
  fs.writeFileSync(MEMORIA_PATH, '');
}

function listarMemoria() {
  return memoria;
}

// Carrega memória logo ao iniciar
carregarMemoria();

module.exports = {
  memoria,
  lembrar,
  salvarMemoria,
  limparMemoria,
  listarMemoria,
  carregarMemoria
};
