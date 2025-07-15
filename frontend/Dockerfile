FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built application
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Create non-root user
RUN addgroup -g 1001 -S nsclc && \
    adduser -S nsclc -u 1001

# Set permissions
RUN chown -R nsclc:nsclc /usr/share/nginx/html && \
    chown -R nsclc:nsclc /var/cache/nginx && \
    chown -R nsclc:nsclc /var/log/nginx && \
    chown -R nsclc:nsclc /etc/nginx/conf.d

# Switch to non-root user
USER nsclc

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"] 