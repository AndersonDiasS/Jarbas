const readline = require('readline');
const fs = require('fs');
const fetch = require('node-fetch'); // aqui fora, uma vez só

const HISTORICO_PATH = './historico_jarbas0.0.1.jsonl';
let memoria = [];

// Carrega histórico
if (fs.existsSync(HISTORICO_PATH)) {
  memoria = JSON.parse(fs.readFileSync(HISTORICO_PATH, 'utf-8'));
  console.log('🧠 Memória carregada com sucesso!');
}

// Salva no disco
function salvarMemoria() {
  fs.writeFileSync(HISTORICO_PATH, JSON.stringify(memoria, null, 2));
}

function lembrar(pergunta, resposta) {
  memoria.push({ tipo: 'mensagem', pergunta, resposta });
  salvarMemoria();
  console.log('📌 Memorizado com sucesso!');
}


function esquecer() {
  memoria = [];
  salvarMemoria();
  console.log('🧹 Memória apagada!');
}

// Função para enviar mensagem ao Ollama
async function perguntarParaIA(input) {
    const mensagens = memoria.map(m => ({
    role: 'user',
    content: m.resposta || m.pergunta || ''
    }));
    mensagens.push({ role: 'user', content: input });

  try {
    const response = await fetch('http://localhost:11434/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'llama3', // ou o modelo que você tiver
        messages: mensagens,
        stream: false
      })
    });

    const data = await response.json();
    console.log(`🤖 ${data.message.content}\n`);
  } catch (error) {
    console.error('Erro ao falar com o Jarbas:', error.message);
  }
}

// Terminal
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function iniciarPrompt() {
  rl.question('Você: ', async (input) => {
    if (input.startsWith('!lembrar')) {
    const texto = input.replace('!lembrar', '').trim();
    if (!texto) {
        console.log('⚠️ Use: !lembrar pergunta | resposta');
    } else {
        const [pergunta, resposta] = texto.split('|').map(s => s.trim());
        lembrar(pergunta || '', resposta || texto);
    }
    return iniciarPrompt();
    }


    if (input === '!esquecer') {
      esquecer();
      return iniciarPrompt();
    }

    if (input === '!listar') {
      console.log('🧠 Lembranças atuais:');
      memoria.forEach((item, index) => {
        console.log(`  ${index + 1}. ${item.texto}`);
      });
      return iniciarPrompt();
    }

    // 👇 Aqui está a chamada para a IA
    await perguntarParaIA(input);
    iniciarPrompt(); // Continua o loop
  });
}

iniciarPrompt();
