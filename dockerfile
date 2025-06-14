# Dockerfile
FROM node:20

# Cria diretório de trabalho
WORKDIR /app

# Copia arquivos do Jarbas
COPY . .

# Instala dependências
RUN npm install

# Expõe a porta (se for servir API futuramente)
EXPOSE 3000

# Inicia o Jarbas (ajuste se for outro arquivo principal)
CMD ["node", "index.js"]
