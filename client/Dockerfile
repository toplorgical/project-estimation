# Development Dockerfile for React-Vite App
FROM node:18-alpine

# Set working directory
WORKDIR /usr/src/app/client

COPY package.json package-lock.json ./
RUN npm ci

# Copy the rest of the application
COPY . .

EXPOSE 8080

# Set environment to development
ENV NODE_ENV=development

CMD ["npm", "run", "build:dev"]