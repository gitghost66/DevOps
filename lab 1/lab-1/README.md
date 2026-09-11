# DevOps Lab 1 — Foundations & Continuous Integration

![CI Pipeline](https://github.com/gitghost66/DevOps/actions/workflows/ci.yml/badge.svg)
![Node.js](https://img.shields.io/badge/Node.js-20.x-green?logo=node.js)
![Jenkins](https://img.shields.io/badge/Jenkins-Declarative%20Pipeline-blue?logo=jenkins)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📋 Lab Overview

**Course:** DevOps Foundations  
**Lab:** Lab 1 — DevOps Foundations & Continuous Integration  
**Environment:** Ubuntu Linux 24.04 LTS  
**Tools:** Git · GitHub · Jenkins · Node.js · Docker · VS Code

This lab demonstrates a complete, production-style DevOps workflow:

- ✅ Git-based source control with a clean, meaningful commit history
- ✅ A working **7-stage Jenkins CI/CD pipeline** (Jenkinsfile)
- ✅ A sample **Node.js/Express** application with unit tests
- ✅ **Docker** containerization with health checks
- ✅ **GitHub Actions** CI as a cloud-hosted mirror of the Jenkins pipeline
- ✅ Full documentation of commands, observations, and pipeline stages

---

## 🗂️ Repository Structure

```
devops-lab1/
├── app/                        # Node.js Express application
│   ├── index.js                #   Main application entry point
│   ├── package.json            #   Dependencies & npm scripts
│   ├── .eslintrc.json          #   ESLint code quality config
│   └── test/
│       └── app.test.js         #   Jest + Supertest unit tests
│
├── docs/                       # Lab documentation
│   ├── COMMANDS.md             #   All commands executed (chronological)
│   ├── PIPELINE_STAGES.md      #   Detailed pipeline stage documentation
│   └── SETUP.md                #   Jenkins & environment setup guide
│
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI workflow
│
├── Jenkinsfile                 # Jenkins declarative pipeline (7 stages)
├── Dockerfile                  # Docker image definition
├── .dockerignore               # Docker build exclusions
├── .gitignore                  # Git exclusions
└── README.md                   # This file
```

---

## 🚀 Application

A lightweight **Node.js/Express** web server that exposes three REST endpoints:

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | App info (name, version, status, timestamp) |
| `/health` | GET | Health check (status, uptime, environment) |
| `/info` | GET | Pipeline metadata |

### Run Locally

```bash
cd app
npm install
npm start
# → App running at http://localhost:3000
```

```bash
# Test the endpoints
curl http://localhost:3000/
curl http://localhost:3000/health
curl http://localhost:3000/info
```

---

## 🔧 Tool Versions

| Tool | Version | Purpose |
|---|---|---|
| Ubuntu | 24.04 LTS | Operating System |
| Git | 2.43.0 | Source control |
| Node.js | 20.x LTS | Application runtime |
| npm | 10.x | Package manager |
| Jenkins | 2.x LTS | CI/CD server |
| Docker | 26.x | Containerization |
| VS Code | 1.90+ | IDE |

---

## 🧪 Tests

```bash
cd app
npm test
```

**Test results:**

```
PASS  test/app.test.js
  DevOps Lab 1 — Express App Tests
    GET /
      ✓ should return 200 with app info JSON
      ✓ should return JSON content-type
    GET /health
      ✓ should return 200 with healthy status
      ✓ should return the current environment
    GET /info
      ✓ should return 200 with pipeline info
    404 handler
      ✓ should return 404 for unknown routes

Test Suites: 1 passed, 1 total
Tests:       6 passed, 6 total
Coverage:    >90%
```

---

## 🏗️ Jenkins CI/CD Pipeline

The `Jenkinsfile` defines a **7-stage declarative pipeline**:

```
Checkout → Install Dependencies → Lint → Test → Build → Docker Build → Deploy
```

| # | Stage | Tool | What Happens |
|---|---|---|---|
| 1 | **Checkout** | Git | Pull latest code from GitHub |
| 2 | **Install Dependencies** | npm ci | Install exact package versions |
| 3 | **Lint** | ESLint | Enforce code quality rules |
| 4 | **Test** | Jest | Run unit tests + coverage report |
| 5 | **Build** | npm | Create production artifact + BUILD_INFO.txt |
| 6 | **Docker Build** | Docker | Build container image |
| 7 | **Deploy** | Docker | Run container, health-check at `/health` |

> See [`docs/PIPELINE_STAGES.md`](docs/PIPELINE_STAGES.md) for detailed stage-by-stage documentation.

---

## 🐳 Docker

### Build Image

```bash
docker build -t devops-lab1-app:latest .
```

### Run Container

```bash
docker run -d \
  --name devops-lab1-app \
  -p 3000:3000 \
  -e NODE_ENV=production \
  devops-lab1-app:latest
```

### Verify

```bash
curl http://localhost:3000/health
docker logs devops-lab1-app
```

### Stop

```bash
docker stop devops-lab1-app && docker rm devops-lab1-app
```

---

## ⚙️ Setup & Configuration

| Guide | Description |
|---|---|
| [`docs/SETUP.md`](docs/SETUP.md) | Jenkins installation, plugin config, job creation, webhook setup |
| [`docs/COMMANDS.md`](docs/COMMANDS.md) | All commands executed during the lab (chronological) |
| [`docs/PIPELINE_STAGES.md`](docs/PIPELINE_STAGES.md) | Detailed pipeline stage explanations |

---

## 📸 Pipeline Screenshots

> _Screenshots of the Jenkins pipeline stages, Blue Ocean view, and test reports go here._
> _Add after running the Jenkins pipeline._

---

## 📝 Observations & Learnings

### Key DevOps Practices Demonstrated

1. **Infrastructure as Code** — Pipeline defined in `Jenkinsfile`, committed to version control
2. **Fail Fast** — Lint and tests run before the expensive Docker Build stage
3. **Reproducibility** — `npm ci` ensures identical dependency installs every run
4. **Security** — Docker container runs as a non-root user
5. **Observability** — Health check endpoint enables automated post-deploy verification
6. **Artifact Management** — `BUILD_INFO.txt` fingerprinted and archived in Jenkins

### Challenges & Solutions

| Challenge | Solution |
|---|---|
| Jenkins can't run Docker by default | Added `jenkins` user to `docker` group |
| Tests affected by running server | Used `module.exports` pattern; only starts server in direct invocation |
| `npm install` vs `npm ci` | Used `npm ci` in CI — cleaner, faster, deterministic |

---

## 🔗 References

- [Jenkins Declarative Pipeline Syntax](https://www.jenkins.io/doc/book/pipeline/syntax/)
- [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Node.js Production Checklist](https://expressjs.com/en/advanced/best-practice-performance.html)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

---

## 👤 Author

**Student Name:** *(your name)*  
**Course:** DevOps Foundations — Lab 1  
**Date:** September 2026
