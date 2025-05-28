const fs = require('fs');
const path = require('path');

// Caminho onde estão os arquivos .jsonl de personalidade
const PERSONALIDADES_PATH = path.join(__dirname, '..', 'personalidades');

let personalidadeAtual = 'jarbas';
let contexto = carregarPersonalidade(personalidadeAtual);

// Padrões para detectar mudança de modo
const interpretacoes = [
  { padrao: /modo\s+or[aá]culo|seja\s+um\s+or[aá]culo/i, nova: 'oraculo' },
  { padrao: /modo\s+sentinela|atue\s+como\s+sentinela/i, nova: 'sentinela' },
  { padrao: /volte\s+ao\s+(modo\s+(jarbas|Jarbas)|modo\s+[a-z]normal)/i, nova: 'jarbas' }
];

function carregarPersonalidade(nome) {
  const arquivo = path.join(PERSONALIDADES_PATH, `${nome}.jsonl`);
  try {
    const linhas = fs.readFileSync(arquivo, 'utf8')
      .split('\n')
      .filter(l => l.trim())
      .map(JSON.parse);
    return linhas;
  } catch (err) {
    console.error(`Erro ao carregar a personalidade "${nome}":`, err.message);
    return [];
  }
}

function verificarMudancaDeModo(input) {
  for (const regra of interpretacoes) {
    if (regra.padrao.test(input)) {
      if (regra.nova !== personalidadeAtual) {
        console.log(`🧠 Mudando para o modo: ${regra.nova}`);
        personalidadeAtual = regra.nova;
        contexto = carregarPersonalidade(personalidadeAtual);
      }
      break;
    }
  }
}

function getContextoAtual() {
  return contexto;
}

function getNomeAtual() {
  return personalidadeAtual;
}

function listarPersonalidades() {
  return fs.readdirSync(PERSONALIDADES_PATH)
    .filter(nome => nome.endsWith('.jsonl'))
    .map(nome => nome.replace('.jsonl', ''));
}

module.exports = {
  verificarMudancaDeModo,
  getContextoAtual,
  getNomeAtual,
  carregarPersonalidade,
  listarPersonalidades
};
