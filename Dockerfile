# Use official Node.js Alpine image
FROM node:22-alpine

# Set working directory
WORKDIR /app

# Set production environment
ENV NODE_ENV=production

# Copy package files
COPY --chown=node:node package*.json ./

# Install production dependencies
RUN npm ci --omit=dev

# Copy application source code
COPY --chown=node:node app.js ./

# Copy frontend files
COPY --chown=node:node public ./public

# Run application as non-root user
USER node

# Application port
EXPOSE 3000

# Start Node.js application
CMD ["node", "app.js"]
