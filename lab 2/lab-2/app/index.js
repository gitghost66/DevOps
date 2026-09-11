'use strict';

const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;
const APP_VERSION = process.env.APP_VERSION || '1.0.0';
const APP_NAME = process.env.APP_NAME || 'devops-lab2-app';

app.use(express.json());

// ── Home route ────────────────────────────────────────────────────────────────
app.get('/', (req, res) => {
  res.status(200).json({
    message: 'DevOps Lab 2 — Containerization & Kubernetes Orchestration',
    app: APP_NAME,
    version: APP_VERSION,
    status: 'running',
    timestamp: new Date().toISOString()
  });
});

// ── Health check (used by Kubernetes liveness & readiness probes) ─────────────
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'healthy',
    uptime: process.uptime(),
    environment: process.env.NODE_ENV || 'development'
  });
});

// ── Version endpoint — changes per deployment to demonstrate rolling updates ──
app.get('/version', (req, res) => {
  res.status(200).json({
    app: APP_NAME,
    version: APP_VERSION,
    node: process.version,
    hostname: require('os').hostname()   // shows which pod is responding
  });
});

// ── Info endpoint ──────────────────────────────────────────────────────────────
app.get('/info', (req, res) => {
  res.status(200).json({
    app: APP_NAME,
    version: APP_VERSION,
    description: 'Sample Node.js app demonstrating Kubernetes orchestration',
    kubernetes: {
      experiments: [
        'Rolling Update Deployment',
        'Blue-Green Deployment',
        'Canary Deployment',
        'Horizontal Scaling',
        'ConfigMap Environment Injection'
      ]
    },
    environment: {
      NODE_ENV: process.env.NODE_ENV || 'development',
      LOG_LEVEL: process.env.LOG_LEVEL || 'info'
    }
  });
});

// ── 404 handler ───────────────────────────────────────────────────────────────
app.use((req, res) => {
  res.status(404).json({ error: 'Route not found' });
});

// ── Start server ──────────────────────────────────────────────────────────────
if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`[${APP_NAME} v${APP_VERSION}] Running at http://localhost:${PORT}`);
    console.log(`[${APP_NAME}] Health check: http://localhost:${PORT}/health`);
    console.log(`[${APP_NAME}] Version info: http://localhost:${PORT}/version`);
    console.log(`[${APP_NAME}] Environment: ${process.env.NODE_ENV || 'development'}`);
  });
}

module.exports = app;
