const express = require('express');
const router = express.Router();
const fetch = require('node-fetch');

const { getContextoAtual, getNomeAtual } = require('../utils/personalidade');
const { adicionarAoHistoricoRecente, carregarHistoricoRecente } = require('../utils/historico');
const { memoria, salvarMemoria } = require('../utils/memoria');

const OLLAMA_URL = process.env.OLLAMA_URL || 'http://ollama:11434';

router.post('/', async (req, res) => {
  const input = req.body.mensagem;

  const historico = carregarHistoricoRecente();

  const mensagens = [
    ...getContextoAtual(),
    ...historico,
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
      const entrada = { role: 'user', content: input };
      const saida = { role: 'assistant', content: resposta };

      adicionarAoHistoricoRecente(entrada);
      adicionarAoHistoricoRecente(saida);

      memoria.push({ tipo: 'mensagem', pergunta: input, resposta });
      salvarMemoria();

      res.json({ resposta });
    } else {
      res.status(204).json({ resposta: null });
    }

  } catch (error) {
    res.status(500).json({ erro: 'Erro ao falar com o Jarbas', detalhe: error.message });
  }
});

module.exports = router;
