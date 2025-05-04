# frontend/Dockerfile

FROM node:23-alpine

WORKDIR /app

# Копируем только package.json (так как yarn.lock отсутствует)
COPY package.json ./

# Устанавливаем зависимости через npm
RUN npm install

# Копируем остальной фронтенд-код
COPY . .

EXPOSE 3000

# Запускаем Vite в режиме разработки на всех интерфейсах
CMD ["npm", "run", "dev", "--", "--host"]
