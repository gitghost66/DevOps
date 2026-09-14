/**
 * k6 Load Test Script – Lab 3
 * Simulates load against the application using k6
 *
 * Usage:
 *   k6 run k6-script.js
 *   k6 run --vus 50 --duration 60s k6-script.js
 *   k6 run --out json=results.json k6-script.js
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// ── Custom Metrics ───────────────────────────────────────────────────────────
const errorRate    = new Rate('error_rate');
const loginLatency = new Trend('login_latency', true);
const apiLatency   = new Trend('api_latency', true);
const pageViews    = new Counter('page_views');

// ── Test Configuration ───────────────────────────────────────────────────────
export const options = {
  // Stages: ramp-up → sustained load → spike → ramp-down
  stages: [
    { duration: '30s',  target: 10  },  // Warm-up
    { duration: '1m',   target: 50  },  // Ramp to 50 VUs
    { duration: '2m',   target: 50  },  // Sustain load
    { duration: '30s',  target: 100 },  // Spike
    { duration: '1m',   target: 100 },  // Sustain spike
    { duration: '30s',  target: 0   },  // Ramp-down
  ],

  thresholds: {
    // 95% of requests must complete within 2s
    'http_req_duration': ['p(95)<2000'],
    // Error rate must stay below 5%
    'error_rate':         ['rate<0.05'],
    // Login must be fast
    'login_latency':      ['p(95)<1000'],
    // API calls must be fast
    'api_latency':        ['p(95)<1500'],
    // HTTP failure rate
    'http_req_failed':    ['rate<0.05'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8080';

// ── Helper Functions ─────────────────────────────────────────────────────────
function randomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

function getAuthToken() {
  const start = Date.now();
  const res = http.post(`${BASE_URL}/api/auth/login`, JSON.stringify({
    username: `user_${randomInt(1, 100)}`,
    password: 'testpassword',
  }), {
    headers: { 'Content-Type': 'application/json' },
    tags: { name: 'login' },
  });

  loginLatency.add(Date.now() - start);

  const ok = check(res, {
    'login status 200': (r) => r.status === 200,
    'login has token':  (r) => r.json('token') !== undefined,
  });

  errorRate.add(!ok);
  return ok ? res.json('token') : null;
}

// ── Main VU Function ─────────────────────────────────────────────────────────
export default function () {
  const token = getAuthToken();
  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type':  'application/json',
  };

  // ── Homepage ──────────────────────────────────────────────────────────────
  group('Homepage', function () {
    const res = http.get(`${BASE_URL}/`, { tags: { name: 'homepage' } });
    pageViews.add(1);
    check(res, {
      'homepage status 200': (r) => r.status === 200,
      'homepage < 1s':       (r) => r.timings.duration < 1000,
    });
    errorRate.add(res.status !== 200);
    sleep(randomInt(1, 2));
  });

  // ── API – Dashboard ────────────────────────────────────────────────────────
  group('API – Dashboard', function () {
    const start = Date.now();
    const res = http.get(`${BASE_URL}/api/dashboard`, {
      headers,
      tags: { name: 'dashboard' },
    });
    apiLatency.add(Date.now() - start);

    const ok = check(res, {
      'dashboard status 200': (r) => r.status === 200 || r.status === 304,
      'dashboard < 2s':       (r) => r.timings.duration < 2000,
    });
    errorRate.add(!ok);
    sleep(randomInt(1, 3));
  });

  // ── API – List Items ───────────────────────────────────────────────────────
  group('API – List Items', function () {
    const page = randomInt(1, 10);
    const start = Date.now();
    const res = http.get(`${BASE_URL}/api/items?page=${page}&limit=20`, {
      headers,
      tags: { name: 'list-items' },
    });
    apiLatency.add(Date.now() - start);

    check(res, {
      'list items status 200': (r) => r.status === 200,
      'list items has data':   (r) => r.json('data') !== undefined,
    });
    sleep(randomInt(1, 2));
  });

  // ── API – Create Item ──────────────────────────────────────────────────────
  if (Math.random() < 0.2) {  // 20% of users create items
    group('API – Create Item', function () {
      const res = http.post(`${BASE_URL}/api/items`, JSON.stringify({
        name:     `Load Test Item ${randomInt(1, 9999)}`,
        value:    Math.random() * 100,
        category: ['A', 'B', 'C'][randomInt(0, 2)],
      }), {
        headers,
        tags: { name: 'create-item' },
      });

      check(res, {
        'create item status 201': (r) => r.status === 201 || r.status === 200,
      });
      sleep(1);
    });
  }

  // ── Health Check ───────────────────────────────────────────────────────────
  group('Health Check', function () {
    const res = http.get(`${BASE_URL}/health`, { tags: { name: 'health' } });
    check(res, {
      'health status 200': (r) => r.status === 200,
      'health body ok':    (r) => r.body.includes('ok') || r.status === 200,
    });
  });

  sleep(randomInt(1, 3));
}

// ── Setup & Teardown ─────────────────────────────────────────────────────────
export function setup() {
  console.log(`\n${'='.repeat(50)}`);
  console.log(`  Lab 3 k6 Load Test`);
  console.log(`  Target: ${BASE_URL}`);
  console.log(`${'='.repeat(50)}\n`);
}

export function teardown(data) {
  console.log('\n✅ k6 load test complete. Check results above.');
}
