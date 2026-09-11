# ─── Build from official Node.js LTS image ────────────────────────────────────
FROM node:20-alpine AS base

# Set working directory inside the container
WORKDIR /usr/src/app

# ─── Install dependencies (cached layer) ──────────────────────────────────────
# Copy only package files first so Docker caches this layer unless deps change
COPY app/package*.json ./
RUN npm ci --omit=dev && npm cache clean --force

# ─── Copy application source ───────────────────────────────────────────────────
COPY app/index.js ./

# ─── Runtime configuration ────────────────────────────────────────────────────
# These defaults are overridden by Kubernetes ConfigMap / env in production
ENV NODE_ENV=production
ENV PORT=3000
ENV APP_VERSION=1.0.0
ENV APP_NAME=devops-lab2-app

EXPOSE 3000

# Add a non-root user for security best practices
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

# Health check — Kubernetes uses /health for liveness & readiness probes
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD wget -qO- http://localhost:3000/health || exit 1

# Start the application
CMD ["node", "index.js"]

# ─── Image metadata ────────────────────────────────────────────────────────────
LABEL maintainer="DevOps Lab Student" \
      version="1.0.0" \
      description="DevOps Lab 2 - Containerization & Kubernetes Orchestration" \
      org.opencontainers.image.title="devops-lab2-app" \
      org.opencontainers.image.version="1.0.0"
