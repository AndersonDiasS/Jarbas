const readline = require('readline');
const fetch = require('node-fetch');
const {
  verificarMudancaDeModo,
  getContextoAtual,
  getNomeAtual,
  listarPersonalidades
} = require('./utils/personalidade');

const { salvarMemoria, carregarMemoria, memoria, listarMemoria } = require('./utils/memoria');

// 🚀 NOVO: Importações para histórico separado
const {
  adicionarÀMemoriaLongoPrazo,
  adicionarAoHistoricoRecente,
  carregarHistoricoRecente
} = require('./utils/historico');

console.log(`🎩 Iniciando Jarbas...`);
console.log(`🤖 Jarbas pronto com a personalidade "${getNomeAtual()}"`);

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  prompt: '> '
});

rl.prompt();

rl.on('line', async (input) => {
  input = input.trim();
  if (!input) return rl.prompt();

  // Comandos Memoria
  if (input === '!memoria') {
    const memoriaList = listarMemoria();
    if (memoriaList.length === 0) {
      console.log('💾 Memória vazia.');
    } else {
      console.log('💾 Memória atual:');
      memoriaList.forEach((item, index) => {
        console.log(`${index + 1}: ${item.pergunta} -> ${item.resposta}`);
      });
    }
    return rl.prompt();
  }

  // Comandos de Personalidade


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

  // 🧠 NOVO: usa apenas o histórico recente
  const historicoRecentes = carregarHistoricoRecente();

  const mensagens = [
    ...getContextoAtual(),
    ...historicoRecentes,
    { role: 'user', content: input }
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

      // 💾 Salva em ambos os históricos
      const entrada = { role: 'user', content: input };
      const saida = { role: 'assistant', content: resposta };

      adicionarAoHistoricoRecente(entrada);
      adicionarAoHistoricoRecente(saida);
      adicionarÀMemoriaLongoPrazo(entrada);
      adicionarÀMemoriaLongoPrazo(saida);

      memoria.push({ tipo: 'mensagem', pergunta: input, resposta });
      salvarMemoria();
    } else {
      console.log('🤖 Jarbas: (sem resposta)');
    }

  } catch (error) {
    console.error('❌ Erro ao falar com o Jarbas:', error.message);
  }

  rl.prompt();
});
