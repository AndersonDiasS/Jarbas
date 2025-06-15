const express = require('express');
const fetch = require('node-fetch');
const cors = require('cors');
const bodyParser = require('body-parser');

const {
  verificarMudancaDeModo,
  getContextoAtual,
  getNomeAtual,
} = require('./utils/personalidade');

const {
  salvarMemoria,
  carregarMemoria,
  memoria,
} = require('./utils/memoria');

const {
  adicionarÀMemoriaLongoPrazo,
  adicionarAoHistoricoRecente,
  carregarHistoricoRecente,
} = require('./utils/historico');

const OLLAMA_URL = process.env.OLLAMA_URL || 'http://ollama:11434';

const app = express();
app.use(cors());
app.use(bodyParser.json());

console.log(`🎩 Iniciando Jarbas...`);
console.log(`🤖 Jarbas pronto com a personalidade "${getNomeAtual()}"`);

app.post('/chat', async (req, res) => {
  try {
    const input = req.body.message?.trim();
    if (!input) return res.status(400).json({ error: 'Mensagem vazia' });

    // Verifica mudança de modo e carrega memória
    verificarMudancaDeModo(input);
    carregarMemoria();

    // Monta contexto + histórico
    const historicoRecentes = carregarHistoricoRecente();
    const mensagens = [...getContextoAtual(), ...historicoRecentes, { role: 'user', content: input }];

    // Chama API Ollama
    const response = await fetch(`${OLLAMA_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'llama3',
        messages: mensagens,
        stream: false,
      }),
    });

    const data = await response.json();
    const resposta = data.message?.content?.trim();

    if (resposta) {
      // Salva histórico e memória
      adicionarAoHistoricoRecente({ role: 'user', content: input });
      adicionarAoHistoricoRecente({ role: 'assistant', content: resposta });
      adicionarÀMemoriaLongoPrazo({ role: 'user', content: input });
      adicionarÀMemoriaLongoPrazo({ role: 'assistant', content: resposta });
      memoria.push({ tipo: 'mensagem', pergunta: input, resposta });
      salvarMemoria();

      res.json({ reply: resposta });
    } else {
      res.json({ reply: '(sem resposta)' });
    }
  } catch (error) {
    console.error('❌ Erro ao falar com o Jarbas:', error.message);
    res.status(500).json({ erro: 'Erro ao falar com o Jarbas', detalhe: error.message });
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`API Jarbas rodando na porta ${PORT}`);
});
