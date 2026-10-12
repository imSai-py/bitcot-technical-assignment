# Node 22 Alpine base image
FROM node:22-alpine

WORKDIR /app

# Install dependencies
COPY package*.json tsconfig.json vitest.config.ts ./
RUN npm ci

# Copy source code and tests
COPY src/ ./src/
COPY tests/ ./tests/

# Compile TypeScript
RUN npm run build

# Default command runs the test suite
CMD ["npm", "test"]
