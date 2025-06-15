const express = require('express');
const router = express.Router();
const { listarMemoria, salvarMemoria, limparMemoria, memoria } = require('../utils/memoria');

router.get('/', (req, res) => {
  res.json(listarMemoria());
});

router.post('/', (req, res) => {
  salvarMemoria();
  res.json({ status: 'Memória salva com sucesso' });
});

router.delete('/', (req, res) => {
  limparMemoria();
  res.json({ status: 'Memória limpa com sucesso' });
});

module.exports = router;
