FROM node:20-alpine

# Installer les dépendances nécessaires pour compiler better-sqlite3
RUN apk add --no-cache python3 make g++

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies et forcer la recompilation de better-sqlite3 pour Alpine
RUN npm install && npm rebuild better-sqlite3

# Copy application code
COPY . .

# Expose port
EXPOSE 3000

# Run the application
CMD ["npm", "run", "dev"]

