# ─── Build from official Node.js LTS image ───────────────────────────────────
FROM node:20-alpine AS base

# Set working directory inside the container
WORKDIR /usr/src/app

# ─── Install dependencies (cached layer) ─────────────────────────────────────
COPY app/package*.json ./
RUN npm ci --omit=dev && npm cache clean --force

# ─── Copy application source ──────────────────────────────────────────────────
COPY app/index.js ./

# ─── Runtime configuration ────────────────────────────────────────────────────
ENV NODE_ENV=production
ENV PORT=3000
EXPOSE 3000

# Add a non-root user for security best practices
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

# Health check — Docker will mark container unhealthy if this fails
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD wget -qO- http://localhost:3000/health || exit 1

# Start the application
CMD ["node", "index.js"]

# ─── Image metadata ───────────────────────────────────────────────────────────
LABEL maintainer="DevOps Lab Student" \
      version="1.0.0" \
      description="DevOps Lab 1 - CI/CD Pipeline Demo App" \
      org.opencontainers.image.title="devops-lab1-app" \
      org.opencontainers.image.version="1.0.0"
