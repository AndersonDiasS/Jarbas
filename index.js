const readline = require('readline');
const fetch = require('node-fetch');
const {
  verificarMudancaDeModo,
  getContextoAtual,
  getNomeAtual,
  listarPersonalidades
} = require('./utils/personalidade');

const {
  criarAnotacao,
  removerAnotacao,
  listarAnotacoes,
  lerAnotacao
} = require('./utils/arquivo');

const { salvarMemoria, carregarMemoria, memoria, listarMemoria, limparMemoria } = require('./utils/memoria');

// 🚀 NOVO: Importações para histórico separado
const {
  adicionarÀMemoriaLongoPrazo,
  adicionarAoHistoricoRecente,
  carregarHistoricoRecente
} = require('./utils/historico');

const OLLAMA_URL = process.env.OLLAMA_URL || 'http://ollama:11434';
 
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

  if (input === '!salvar') {
    salvarMemoria();
    console.log('💾 Memória salva com sucesso!');
    return rl.prompt();
  }

  if (input === '!limpar') {
    limparMemoria();
    console.log('🗑️ Memória limpa com sucesso!');
    return rl.prompt();
  }

  // Criação Remoção ou edição de arquivos 
  
async function interpretarComandoNatural(input) {
  const texto = input.toLowerCase();

    if (texto.includes('anote') || texto.includes('crie uma nota') || texto.includes('criar nota')) {
      await criarAnotacao(input);
      console.log('📝 Anotação criada com sucesso!');
      return true;
    }

    if (texto.includes('delete') || texto.includes('remova') || texto.includes('exclua')) {
      const ok = await removerAnotacao(input);
      console.log(ok ? '🗑️ Nota removida com sucesso!' : '⚠️ Nenhuma nota correspondente encontrada.');
      return true;
    }

    if (texto.includes('mostrar notas') || texto.includes('anotações') || texto.includes('listar notas')) {
      const notas = await listarAnotacoes();
      if (notas.length === 0) {
        console.log('📭 Nenhuma anotação encontrada.');
      } else {
        console.log('🗂️ Anotações:');
        notas.forEach((n, i) => console.log(` ${i + 1}. ${n}`));
      }
      return true;
    }

    if (texto.includes('ler nota') || texto.includes('leia a nota') || texto.includes('mostre a nota')) {
      const conteudo = await lerAnotacao(input);
      if (conteudo) {
        console.log('📄 Conteúdo da nota:\n', conteudo);
      } else {
        console.log('⚠️ Nenhuma nota correspondente encontrada.');
      }
      return true;
    }

    return false;
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
    const response = await fetch(`${OLLAMA_URL}/api/chat`, {
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
