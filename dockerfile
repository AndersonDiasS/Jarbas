# Usa imagem Node 20
FROM node:20

# Define diretório de trabalho
WORKDIR /app

# Copia só o package.json e package-lock.json primeiro
COPY package*.json ./

# Instala dependências com cache
RUN npm install

# Agora copia o restante do projeto
COPY . .

# Expõe a porta (pode ajustar se necessário)
EXPOSE 3000

# Comando padrão para iniciar o Jarbas
CMD ["npm", "run", "jarbas"]
