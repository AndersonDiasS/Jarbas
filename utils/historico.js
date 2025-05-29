const fs = require('fs');
const path = require('path');

// Caminho correto, relativo à raiz do projeto (index.js está na raiz)
const CAMINHO_MEMORIA = path.resolve(__dirname, '../historicos/memoria.jsonl');
const CAMINHO_RECENTE = path.resolve(__dirname, '../historicos/memoria-curto-prazo.jsonl');

const LIMITE_RECENTE = 10;

function adicionarÀMemoriaLongoPrazo(mensagem) {
  const linha = JSON.stringify(mensagem) + '\n';
  fs.appendFileSync(CAMINHO_MEMORIA, linha);
}

function adicionarAoHistoricoRecente(mensagem) {
  let historico = [];

  if (fs.existsSync(CAMINHO_RECENTE)) {
    historico = fs.readFileSync(CAMINHO_RECENTE, 'utf-8')
      .split('\n')
      .filter(l => l.trim())
      .map(JSON.parse);
  }

  historico.push(mensagem);

  if (historico.length > LIMITE_RECENTE) {
    historico = historico.slice(-LIMITE_RECENTE);
  }

  fs.writeFileSync(CAMINHO_RECENTE, historico.map(m => JSON.stringify(m)).join('\n') + '\n');
}

function carregarHistoricoRecente() {
  if (!fs.existsSync(CAMINHO_RECENTE)) return [];
  return fs.readFileSync(CAMINHO_RECENTE, 'utf-8')
    .split('\n')
    .filter(l => l.trim())
    .map(JSON.parse);
}

module.exports = {
  adicionarÀMemoriaLongoPrazo,
  adicionarAoHistoricoRecente,
  carregarHistoricoRecente
};
