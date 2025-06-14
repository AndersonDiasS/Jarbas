// utils/arquivo.js

const fs = require('fs');
const path = require('path');
const pastaArquivos = path.join(__dirname, '../historico/arquivos');

if (!fs.existsSync(pastaArquivos)) fs.mkdirSync(pastaArquivos, { recursive: true });

function gerarNomeArquivo(frase) {
  return frase
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, '')
    .split(' ')
    .slice(0, 5)
    .join('-') + '.txt';
}

function criarArquivo(nome, conteudo) {
  const caminho = path.join(pastaArquivos, nome);
  fs.writeFileSync(caminho, conteudo);
}

function removerArquivo(nome) {
  const caminho = path.join(pastaArquivos, nome);
  if (fs.existsSync(caminho)) fs.unlinkSync(caminho);
}

function listarArquivos() {
  return fs.readdirSync(pastaArquivos);
}

function lerArquivo(nome) {
  const caminho = path.join(pastaArquivos, nome);
  if (fs.existsSync(caminho)) return fs.readFileSync(caminho, 'utf8');
  return null;
}

function interpretarFraseEManipularArquivo(frase) {
  const criarRegex = /(?:anote|crie|registre) (?:que|isso)?(.+)/i;
  const apagarRegex = /(?:apague|delete|remova) (?:a anotacao|a nota)? (?:sobre )?(.+)/i;
  const lerRegex = /(?:leia|mostre|lembre|abra) (?:a anotacao|a nota)? (?:sobre )?(.+)/i;
  const listarRegex = /quais (?:anotacoes|notas) eu tenho/i;

  if (listarRegex.test(frase)) return { tipo: 'listar' };

  let match;
  if ((match = criarRegex.exec(frase))) {
    const conteudo = match[1].trim();
    const nome = gerarNomeArquivo(conteudo);
    return { tipo: 'criar', nomeArquivo: nome, conteudo };
  }

  if ((match = apagarRegex.exec(frase))) {
    const referencia = match[1].trim();
    const nome = gerarNomeArquivo(referencia);
    return { tipo: 'remover', nomeArquivo: nome };
  }

  if ((match = lerRegex.exec(frase))) {
    const referencia = match[1].trim();
    const nome = gerarNomeArquivo(referencia);
    return { tipo: 'ler', nomeArquivo: nome };
  }

  return null;
}

module.exports = {
  criarArquivo,
  removerArquivo,
  listarArquivos,
  lerArquivo,
  interpretarFraseEManipularArquivo
};
