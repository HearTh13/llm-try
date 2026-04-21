# Gunakan Node.js untuk lingkungan pengembangan (mendukung HMR)
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 5173
# Default command untuk dev mode
CMD ["npm", "run", "dev"]
