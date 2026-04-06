FROM node:20-alpine

WORKDIR /app

# Copy package files first for better layer caching
COPY frontend/package.json frontend/package-lock.json* ./

# Install dependencies
RUN npm install

# Copy the rest of the application
COPY frontend/ .

# Expose Next.js dev server port
EXPOSE 3000

# Bind to all interfaces so Docker can forward traffic
ENV HOSTNAME="0.0.0.0"

# Start the development server
CMD ["npm", "run", "dev"]
