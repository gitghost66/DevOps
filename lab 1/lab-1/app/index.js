'use strict';

const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

// Home route
app.get('/', (req, res) => {
  res.status(200).json({
    message: 'DevOps Lab 1 — CI/CD Pipeline Demo App',
    status: 'running',
    version: '1.0.0',
    timestamp: new Date().toISOString()
  });
});

// Health check endpoint (used by Jenkins post-deploy verification)
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'healthy',
    uptime: process.uptime(),
    environment: process.env.NODE_ENV || 'development'
  });
});

// Info endpoint
app.get('/info', (req, res) => {
  res.status(200).json({
    app: 'devops-lab1-app',
    description: 'Sample Node.js app demonstrating CI/CD with Jenkins',
    pipeline: {
      stages: ['Checkout', 'Install', 'Lint', 'Test', 'Build', 'Docker Build', 'Deploy'],
      tool: 'Jenkins'
    }
  });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: 'Route not found' });
});

// Only start the server if this file is run directly (not imported in tests)
if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`[DevOps Lab 1] App running at http://localhost:${PORT}`);
    console.log(`[DevOps Lab 1] Health check: http://localhost:${PORT}/health`);
    console.log(`[DevOps Lab 1] Environment: ${process.env.NODE_ENV || 'development'}`);
  });
}

module.exports = app;
