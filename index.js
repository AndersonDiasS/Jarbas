// import readline from 'readline';
// import { listarPersonalidadesDisponiveis, carregarPersonalidade } from './utils/personalidade.js';
// import { carregarHistorico, salvarNoHistorico } from './utils/historico.js';


// const mensagens = [];

// async function conversarComIA(input) {
//   mensagens.push({ role: 'user', content: input });

//   try {
//     const response = await fetch('http://localhost:11434/api/chat', {
//       method: 'POST',
//       headers: { 'Content-Type': 'application/json' },
//       body: JSON.stringify({
//         model: 'llama3',
//         messages: mensagens,
//         stream: false
//       })
//     });

//     const data = await response.json();
//     const resposta = data.message?.content?.trim();

//     if (resposta) {
//       mensagens.push({ role: 'assistant', content: resposta });
//       salvarNoHistorico({ pergunta: input, resposta });
//       console.log(`🤖 Jarbas: ${resposta}\n`);
//     } else {
//       console.log('🤖 (sem resposta)\n');
//     }
//   } catch (err) {
//     console.error('❌ Erro ao falar com o Jarbas:', err.message);
//   }
// }

// async function iniciarJarbas() {
//   console.log('🎩 Iniciando Jarbas...');

//   const opcoes = listarPersonalidadesDisponiveis();
//   console.log(`🧠 Personalidades disponíveis: ${opcoes.join(', ')}`);
//   const escolhida = opcoes.includes('jarbas') ? 'jarbas' : opcoes[0]; // pode adaptar para prompt futuramente

//   const personalidade = carregarPersonalidade(escolhida);
//   mensagens.push(...personalidade);

//   const historico = carregarHistorico();
//   historico.forEach(h => {
//     mensagens.push({ role: 'user', content: h.pergunta });
//     mensagens.push({ role: 'assistant', content: h.resposta });
//   });

//   console.log(`🤖 Jarbas pronto com a personalidade "${escolhida}".\n`);

//   const rl = readline.createInterface({
//     input: process.stdin,
//     output: process.stdout,
//     prompt: '> '
//   });

//   rl.prompt();
//   rl.on('line', async (line) => {
//     const input = line.trim();
//     if (!input) return rl.prompt();
//     await conversarComIA(input);
//     rl.prompt();
//   });
// }

// iniciarJarbas();
const readline = require('readline');
const fetch = require('node-fetch');
const {
  verificarMudancaDeModo,
  getContextoAtual,
  getNomeAtual,
  listarPersonalidades
} = require('./utils/personalidade');
 
const { salvarMemoria, carregarMemoria, memoria } = require('./utils/memoria');
const { carregarHistorico, salvarNoHistorico } = require('./utils/historico');

console.log(`🎩 Iniciando Jarbas...`);
console.log(`🤖 Jarbas pronto com a personalidade "${getNomeAtual()}".`);

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  prompt: '> '
});

rl.prompt();

rl.on('line', async (input) => {
  input = input.trim();
  if (!input) return rl.prompt();

  if (input === '!personalidades') {
    const modos = listarPersonalidades();
    console.log('🎭 Personalidades disponíveis:', modos.join(', '));
    return rl.prompt();
  }

  if (input === '!modoatual') {
    console.log(`🧠 Modo atual: ${getNomeAtual()}`);
    return rl.prompt();
  }

  // Verifica se o usuário quer mudar de personalidade
  verificarMudancaDeModo(input);
  carregarMemoria();
  const historicoCompleto = carregarHistorico();
  const historicoRecentes = historicoCompleto.slice(-50).flatMap((registro) => [
    { role: 'user', content: registro.pergunta },
    { role: 'assistant', content: registro.resposta }
  ]);

  // Define o contexto total da requisição
  const mensagens = [
    ...getContextoAtual(), // contexto da personalidade atual
    ...historicoRecentes,  // últimas interações
    { role: 'user', content: input } // entrada atual
  ];

  try {
    const response = await fetch('http://localhost:11434/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'llama3',
        messages: mensagens,
        stream: false
      })
    });

    const data = await response.json();
    const resposta = data.message?.content?.trim();

    if (resposta) {
      console.log(`🤖 Jarbas: ${resposta}`);

      // Salva em memória e histórico
      memoria.push({ tipo: 'mensagem', pergunta: input, resposta });
      salvarMemoria();
      salvarNoHistorico({ pergunta: input, resposta });
    } else {
      console.log('🤖 Jarbas: (sem resposta)');
    }

  } catch (error) {
    console.error('❌ Erro ao falar com o Jarbas:', error.message);
  }

  rl.prompt();
});
