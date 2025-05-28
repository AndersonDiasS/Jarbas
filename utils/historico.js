const fs = require('fs');
const path = require('path');

const HISTORICO_PATH = path.resolve('historicos/geral.jsonl');

function carregarHistorico(limit = 5) {
  if (!fs.existsSync(HISTORICO_PATH)) return [];

  const linhas = fs.readFileSync(HISTORICO_PATH, 'utf8')
    .split('\n')
    .filter(l => l.trim())
    .map(JSON.parse);

  return linhas.slice(-limit);
}

function salvarNoHistorico(mensagem) {
  fs.appendFileSync(HISTORICO_PATH, JSON.stringify(mensagem) + '\n');
}

module.exports = {
  carregarHistorico,
  salvarNoHistorico
};
