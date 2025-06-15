const express = require('express');
const router = express.Router();
const { getNomeAtual, listarPersonalidades } = require('../utils/personalidade');

router.get('/', (req, res) => {
  res.json({
    atual: getNomeAtual(),
    disponiveis: listarPersonalidades()
  });
});

module.exports = router;
