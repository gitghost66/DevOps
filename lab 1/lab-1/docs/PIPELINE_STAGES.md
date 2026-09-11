# Jenkins Pipeline Stages — DevOps Lab 1

> Detailed documentation of each stage in the `Jenkinsfile` declarative pipeline.

---

## Pipeline Overview

```
┌────────────┐   ┌─────────────┐   ┌──────┐   ┌──────┐   ┌───────┐   ┌──────────────┐   ┌────────┐
│  Checkout  │──▶│  Install    │──▶│ Lint │──▶│ Test │──▶│ Build │──▶│ Docker Build │──▶│ Deploy │
└────────────┘   └─────────────┘   └──────┘   └──────┘   └───────┘   └──────────────┘   └────────┘
```

**Total Stages:** 7  
**Tool:** Jenkins Declarative Pipeline  
**Agent:** `any` (runs on any available Jenkins node)

---

## Stage 1 — Checkout

| Property | Value |
|---|---|
| Purpose | Pull latest source code from GitHub |
| Command | `checkout scm` |
| Output | Source code available in Jenkins workspace |

Jenkins automatically clones/pulls from the GitHub repository configured in the job. Git metadata (branch, commit hash, author) is printed for traceability.

---

## Stage 2 — Install Dependencies

| Property | Value |
|---|---|
| Purpose | Install all Node.js packages |
| Command | `npm ci` |
| Directory | `app/` |

`npm ci` is used instead of `npm install` because it:
- Installs exact versions from `package-lock.json`
- Fails if `package-lock.json` is out of sync
- Does not modify any files
- Is faster and more reliable in CI environments

---

## Stage 3 — Lint

| Property | Value |
|---|---|
| Purpose | Enforce code quality and style |
| Command | `npm run lint` (ESLint) |
| Config | `app/.eslintrc.json` |

ESLint checks for:
- Unused variables
- Missing semicolons
- Incorrect indentation
- Trailing spaces
- Quote consistency

If any lint error is found, the stage **fails** and the pipeline stops.

---

## Stage 4 — Test

| Property | Value |
|---|---|
| Purpose | Run unit tests and generate coverage |
| Command | `npm test` (Jest + Supertest) |
| Coverage | `app/coverage/` |
| Test file | `app/test/app.test.js` |

**Tests cover:**
- `GET /` — returns 200 with app info
- `GET /health` — returns 200 with uptime
- `GET /info` — returns pipeline metadata
- `GET /unknown` — returns 404

---

## Stage 5 — Build

| Property | Value |
|---|---|
| Purpose | Create a production-ready artifact |
| Output | `build/` directory + `BUILD_INFO.txt` |
| Archived | `BUILD_INFO.txt` (fingerprinted in Jenkins) |

Installs only production dependencies (`--omit=dev`) and records build metadata (version, build number, git commit, timestamp).

---

## Stage 6 — Docker Build

| Property | Value |
|---|---|
| Purpose | Containerize the application |
| Command | `docker build -t devops-lab1-app:<BUILD_NUMBER> .` |
| Base Image | `node:20-alpine` |
| Exposed Port | `3000` |
| Security | Runs as non-root user (`appuser`) |
| Health check | `HEALTHCHECK` instruction in Dockerfile |

---

## Stage 7 — Deploy

| Property | Value |
|---|---|
| Purpose | Run the Docker container (simulated production deploy) |
| Command | `docker run -d --name devops-lab1-app -p 3000:3000 ...` |
| Verification | `curl http://localhost:3000/health` |

Any previously running container is stopped and removed before the new one starts. A 5-second wait ensures the app is ready before the health check.

---

## Post Actions

| Condition | Action |
|---|---|
| `success` | Print success banner with build number |
| `failure` | Print failure banner with remediation hint |
| `always` | Clean up `build/` directory |
