'use strict';

const request = require('supertest');
const app = require('../index');

describe('DevOps Lab 1 — Express App Tests', () => {

  // ── GET / ──────────────────────────────────────────────────────────────────
  describe('GET /', () => {
    it('should return 200 with app info JSON', async () => {
      const res = await request(app).get('/');
      expect(res.statusCode).toBe(200);
      expect(res.body).toHaveProperty('message');
      expect(res.body).toHaveProperty('status', 'running');
      expect(res.body).toHaveProperty('version', '1.0.0');
      expect(res.body).toHaveProperty('timestamp');
    });

    it('should return JSON content-type', async () => {
      const res = await request(app).get('/');
      expect(res.headers['content-type']).toMatch(/json/);
    });
  });

  // ── GET /health ────────────────────────────────────────────────────────────
  describe('GET /health', () => {
    it('should return 200 with healthy status', async () => {
      const res = await request(app).get('/health');
      expect(res.statusCode).toBe(200);
      expect(res.body).toHaveProperty('status', 'healthy');
      expect(res.body).toHaveProperty('uptime');
      expect(typeof res.body.uptime).toBe('number');
    });

    it('should return the current environment', async () => {
      const res = await request(app).get('/health');
      expect(res.body).toHaveProperty('environment');
    });
  });

  // ── GET /info ──────────────────────────────────────────────────────────────
  describe('GET /info', () => {
    it('should return 200 with pipeline info', async () => {
      const res = await request(app).get('/info');
      expect(res.statusCode).toBe(200);
      expect(res.body).toHaveProperty('app', 'devops-lab1-app');
      expect(res.body.pipeline).toHaveProperty('tool', 'Jenkins');
      expect(Array.isArray(res.body.pipeline.stages)).toBe(true);
      expect(res.body.pipeline.stages.length).toBeGreaterThan(0);
    });
  });

  // ── 404 handler ───────────────────────────────────────────────────────────
  describe('404 handler', () => {
    it('should return 404 for unknown routes', async () => {
      const res = await request(app).get('/unknown-route');
      expect(res.statusCode).toBe(404);
      expect(res.body).toHaveProperty('error', 'Route not found');
    });
  });

});
