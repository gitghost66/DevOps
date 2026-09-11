# Lab 2 — Containerization & Kubernetes Orchestration

> **Course:** DevOps | **Student:** gitghost66  
> **Tools:** Docker · Docker Compose · Minikube · kubectl

---

## 📋 Objective

Develop a containerized application workflow and orchestrate its deployment using Kubernetes. This lab demonstrates:

- Building and managing Docker container images
- Multi-container orchestration with Docker Compose
- Deploying, scaling, and updating applications on a Kubernetes (Minikube) cluster
- Applying deployment strategies: **Rolling Update**, **Blue-Green**, and **Canary**
- Injecting configuration via Kubernetes **ConfigMaps**

---

## 📁 Repository Structure

```
lab-2/
├── app/
│   ├── index.js              ← Node.js Express app (v1/v2)
│   └── package.json
├── Dockerfile                ← Multi-layer, secure Node.js image
├── .dockerignore
├── docker-compose.yml        ← Multi-container local setup (app + Redis)
├── k8s/
│   ├── configmap.yaml        ← App configuration (env vars)
│   ├── deployment.yaml       ← v1.0.0 — Rolling update base
│   ├── deployment-v2.yaml    ← v2.0.0 — Rolling update target
│   ├── service.yaml          ← NodePort Service (port 30080)
│   ├── blue-green/
│   │   ├── blue-deployment.yaml   ← Stable slot (v1.0.0)
│   │   ├── green-deployment.yaml  ← New slot (v2.0.0)
│   │   └── service.yaml           ← Traffic switch service (port 30081)
│   └── canary/
│       ├── stable-deployment.yaml ← 9 replicas, ~90% traffic (v1.0.0)
│       └── canary-deployment.yaml ← 1 replica,  ~10% traffic (v2.0.0)
└── README.md
```

---

## 🚀 Experiments

---

### Experiment 1 — Docker Image Management

**Objective:** Build, tag, inspect, and manage Docker images.

#### Step 1 — Build the Docker image

```bash
# Navigate to the lab-2 directory
cd lab-2

# Build the image (v1.0.0)
docker build -t devops-lab2-app:1.0.0 .
```

**Expected output:**
```
[+] Building 12.4s (9/9) FINISHED
 => [base 1/4] FROM node:20-alpine
 => [base 2/4] WORKDIR /usr/src/app
 => [base 3/4] COPY app/package*.json ./
 => [base 4/4] RUN npm ci --omit=dev && npm cache clean --force
 => COPY app/index.js ./
 => RUN addgroup -S appgroup && adduser -S appuser -G appgroup
 => exporting to image
Successfully built <image-id>
Successfully tagged devops-lab2-app:1.0.0
```

#### Step 2 — Inspect and list images

```bash
# List all local images
docker images

# Inspect the image metadata
docker inspect devops-lab2-app:1.0.0
```

**Expected output (`docker images`):**
```
REPOSITORY          TAG       IMAGE ID       CREATED          SIZE
devops-lab2-app     1.0.0     a3c9f1b2e4d1   30 seconds ago   120MB
```

#### Step 3 — Run the container

```bash
# Run container and map port 3000
docker run -d --name lab2-container -p 3000:3000 devops-lab2-app:1.0.0

# Check container is running
docker ps

# Test the app
curl http://localhost:3000
curl http://localhost:3000/health
curl http://localhost:3000/version
```

**Expected output (`curl http://localhost:3000`):**
```json
{
  "message": "DevOps Lab 2 — Containerization & Kubernetes Orchestration",
  "app": "devops-lab2-app",
  "version": "1.0.0",
  "status": "running",
  "timestamp": "2024-09-08T04:11:00.000Z"
}
```

#### Step 4 — Container lifecycle commands

```bash
# View logs
docker logs lab2-container

# Stop the container
docker stop lab2-container

# Remove the container
docker rm lab2-container

# Tag image for a registry (e.g., Docker Hub)
docker tag devops-lab2-app:1.0.0 gitghost66/devops-lab2-app:1.0.0
```

---

### Experiment 2 — Docker Compose (Multi-Container)

**Objective:** Orchestrate the app alongside a Redis service using Docker Compose.

#### Step 1 — Start all services

```bash
docker compose up -d
```

**Expected output:**
```
[+] Running 3/3
 ✔ Network lab-2_lab2-network   Created
 ✔ Container lab2-redis         Healthy
 ✔ Container lab2-app           Started
```

#### Step 2 — Verify services

```bash
# List running containers
docker compose ps

# Check application logs
docker compose logs app

# Test the app
curl http://localhost:3000/info
```

**Expected output (`docker compose ps`):**
```
NAME           IMAGE                    STATUS
lab2-app       devops-lab2-app:1.0.0   Up (healthy)
lab2-redis     redis:7-alpine           Up (healthy)
```

#### Step 3 — Tear down

```bash
docker compose down
docker compose down -v   # also removes named volumes
```

---

### Experiment 3 — Kubernetes Deployment & ConfigMap

**Objective:** Deploy the app on Minikube, inject configuration via ConfigMap.

#### Step 1 — Start Minikube

```bash
minikube start
minikube status
```

**Expected output:**
```
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
```

#### Step 2 — Build image inside Minikube's Docker daemon

```bash
# Point local Docker CLI to Minikube's Docker daemon
eval $(minikube docker-env)        # Linux/macOS
# On Windows PowerShell:
# & minikube -p minikube docker-env | Invoke-Expression

# Build the image (now available inside Minikube)
docker build -t devops-lab2-app:1.0.0 .
docker build -t devops-lab2-app:2.0.0 .   # build v2 for later experiments
```

#### Step 3 — Apply ConfigMap

```bash
kubectl apply -f k8s/configmap.yaml
kubectl describe configmap lab2-app-config
```

**Expected output:**
```
Name:         lab2-app-config
Namespace:    default
Data
====
APP_NAME:      devops-lab2-app
APP_VERSION:   1.0.0
LOG_LEVEL:     info
NODE_ENV:      production
PORT:          3000
```

#### Step 4 — Deploy the application

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Watch pods come up
kubectl get pods -w
```

**Expected output:**
```
NAME                        READY   STATUS    RESTARTS   AGE
lab2-app-7d9f8c4b5-2xkpq   1/1     Running   0          30s
lab2-app-7d9f8c4b5-8mnvt   1/1     Running   0          30s
lab2-app-7d9f8c4b5-kqrtl   1/1     Running   0          30s
```

#### Step 5 — Access the application

```bash
# Get the Minikube service URL
minikube service lab2-app-service --url

# Test the endpoint (replace with URL from above)
curl http://<minikube-ip>:30080
curl http://<minikube-ip>:30080/version
```

**Expected `/version` response:**
```json
{
  "app": "devops-lab2-app",
  "version": "1.0.0",
  "node": "v20.x.x",
  "hostname": "lab2-app-7d9f8c4b5-2xkpq"
}
```

> **Observation:** The `hostname` field shows the pod name, proving which pod handled the request.

---

### Experiment 4 — Rolling Update Deployment

**Objective:** Update the application from v1.0.0 to v2.0.0 with zero downtime.

#### Step 1 — Verify current version

```bash
curl http://<minikube-ip>:30080/version
# Expected: "version": "1.0.0"
```

#### Step 2 — Apply the v2 deployment

```bash
kubectl apply -f k8s/deployment-v2.yaml
```

#### Step 3 — Watch the rolling update

```bash
# Watch the rollout progress
kubectl rollout status deployment/lab2-app

# Watch pods being replaced (open a second terminal)
kubectl get pods -w
```

**Expected rollout output:**
```
Waiting for deployment "lab2-app" rollout to finish: 1 out of 3 new replicas have been updated...
Waiting for deployment "lab2-app" rollout to finish: 2 out of 3 new replicas have been updated...
Waiting for deployment "lab2-app" rollout to finish: 1 old replicas are pending termination...
deployment "lab2-app" successfully rolled out
```

#### Step 4 — Verify updated version

```bash
curl http://<minikube-ip>:30080/version
# Expected: "version": "2.0.0"
```

#### Step 5 — View rollout history

```bash
kubectl rollout history deployment/lab2-app
```

**Expected output:**
```
REVISION  CHANGE-CAUSE
1         Initial deployment v1.0.0
2         Rolling update to v2.0.0 — new /version endpoint
```

#### Step 6 — Rollback

```bash
kubectl rollout undo deployment/lab2-app
kubectl rollout status deployment/lab2-app
curl http://<minikube-ip>:30080/version
# Expected: "version": "1.0.0"
```

---

### Experiment 5 — Horizontal Scaling

**Objective:** Scale the deployment up and down manually.

```bash
# Scale up to 5 replicas
kubectl scale deployment lab2-app --replicas=5
kubectl get pods

# Scale down to 2 replicas
kubectl scale deployment lab2-app --replicas=2
kubectl get pods
```

**Expected output (after scale up):**
```
NAME                        READY   STATUS    RESTARTS   AGE
lab2-app-7d9f8c4b5-2xkpq   1/1     Running   0          5m
lab2-app-7d9f8c4b5-8mnvt   1/1     Running   0          5m
lab2-app-7d9f8c4b5-kqrtl   1/1     Running   0          5m
lab2-app-7d9f8c4b5-pqrst   1/1     Running   0          10s   ← new
lab2-app-7d9f8c4b5-uvwxy   1/1     Running   0          10s   ← new
```

> **Observation:** New pods are ready in seconds due to the lightweight container image.

---

### Experiment 6 — Blue-Green Deployment

**Objective:** Switch all traffic from v1.0.0 (blue) to v2.0.0 (green) instantly with zero downtime and easy rollback.

#### Step 1 — Deploy both environments

```bash
kubectl apply -f k8s/blue-green/blue-deployment.yaml
kubectl apply -f k8s/blue-green/green-deployment.yaml
kubectl apply -f k8s/blue-green/service.yaml

kubectl get pods -l app=lab2-app
```

**Expected output:**
```
NAME                             READY   STATUS    AGE
lab2-app-blue-7d6f4c-2xkpq      1/1     Running   1m   ← blue slot
lab2-app-blue-7d6f4c-8mnvt      1/1     Running   1m
lab2-app-blue-7d6f4c-kqrtl      1/1     Running   1m
lab2-app-green-9f8b2d-pqrst     1/1     Running   1m   ← green slot
lab2-app-green-9f8b2d-uvwxy     1/1     Running   1m
lab2-app-green-9f8b2d-wxyz1     1/1     Running   1m
```

#### Step 2 — Verify traffic goes to blue (v1.0.0)

```bash
curl http://<minikube-ip>:30081/version
# Expected: "version": "1.0.0"
```

#### Step 3 — Cut over to green (instant switch)

```bash
kubectl patch service lab2-app-bg-service \
  -p '{"spec":{"selector":{"app":"lab2-app","slot":"green"}}}'
```

#### Step 4 — Verify traffic now goes to green (v2.0.0)

```bash
curl http://<minikube-ip>:30081/version
# Expected: "version": "2.0.0"
```

#### Step 5 — Rollback to blue (instant)

```bash
kubectl patch service lab2-app-bg-service \
  -p '{"spec":{"selector":{"app":"lab2-app","slot":"blue"}}}'

curl http://<minikube-ip>:30081/version
# Expected: "version": "1.0.0"
```

> **Key difference from Rolling Update:** Blue-Green is an **instant** all-or-nothing switch, while Rolling Update gradually replaces pods. Blue-Green also keeps the old environment running for immediate rollback.

---

### Experiment 7 — Canary Deployment

**Objective:** Route ~10% of traffic to v2.0.0 (canary) while 90% continues on v1.0.0 (stable).

#### Step 1 — Deploy stable (9 replicas) and canary (1 replica)

```bash
kubectl apply -f k8s/canary/stable-deployment.yaml
kubectl apply -f k8s/canary/canary-deployment.yaml

kubectl get pods -l app=lab2-app
```

**Expected output:**
```
NAME                               READY   STATUS    AGE
lab2-app-stable-7d6f4c-2xkpq      1/1     Running   1m
lab2-app-stable-7d6f4c-8mnvt      1/1     Running   1m
lab2-app-stable-7d6f4c-kqrtl      1/1     Running   1m
lab2-app-stable-7d6f4c-pqrst      1/1     Running   1m
lab2-app-stable-7d6f4c-uvwxy      1/1     Running   1m
lab2-app-stable-7d6f4c-wxyz1      1/1     Running   1m
lab2-app-stable-7d6f4c-abcde      1/1     Running   1m
lab2-app-stable-7d6f4c-fghij      1/1     Running   1m
lab2-app-stable-7d6f4c-klmno      1/1     Running   1m
lab2-app-canary-9f8b2d-rstuw      1/1     Running   30s   ← canary (1 pod)
```

> **Note:** The canary Service uses the same rolling-update Service (`lab2-app-service` on port 30080) so both `stable` and `canary` pods are in the same endpoint pool.

#### Step 2 — Send repeated requests to observe traffic split

```bash
# Run 10 requests and observe version distribution
for i in {1..10}; do
  curl -s http://<minikube-ip>:30080/version | grep version
done
```

**Expected output (approximately):**
```
"version": "1.0.0"
"version": "1.0.0"
"version": "1.0.0"
"version": "2.0.0"   ← canary hit (~10%)
"version": "1.0.0"
"version": "1.0.0"
"version": "1.0.0"
"version": "1.0.0"
"version": "1.0.0"
"version": "1.0.0"
```

#### Step 3 — Promote canary (if healthy) or rollback

```bash
# Promote: scale canary up to 9, scale stable down to 1
kubectl scale deployment lab2-app-canary  --replicas=9
kubectl scale deployment lab2-app-stable  --replicas=1

# OR rollback: delete canary deployment entirely
kubectl delete deployment lab2-app-canary
```

---

## 🔑 Key Commands Reference

| Action | Command |
|---|---|
| Build image | `docker build -t devops-lab2-app:1.0.0 .` |
| Run container | `docker run -d -p 3000:3000 devops-lab2-app:1.0.0` |
| Start Compose | `docker compose up -d` |
| Start Minikube | `minikube start` |
| Use Minikube Docker | `eval $(minikube docker-env)` |
| Apply manifest | `kubectl apply -f <file>.yaml` |
| Get pods | `kubectl get pods` |
| Watch rollout | `kubectl rollout status deployment/lab2-app` |
| View rollout history | `kubectl rollout history deployment/lab2-app` |
| Rollback | `kubectl rollout undo deployment/lab2-app` |
| Scale replicas | `kubectl scale deployment lab2-app --replicas=5` |
| Patch Service selector | `kubectl patch service <name> -p '{"spec":{"selector":{...}}}'` |
| Delete deployment | `kubectl delete deployment <name>` |
| View ConfigMap | `kubectl describe configmap lab2-app-config` |
| Get service URL | `minikube service lab2-app-service --url` |

---

## 🛠️ Tools Used

![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?logo=kubernetes&logoColor=white)
![Minikube](https://img.shields.io/badge/Minikube-F7B93E?logo=kubernetes&logoColor=black)
![Node.js](https://img.shields.io/badge/Node.js-339933?logo=node.js&logoColor=white)
![Ubuntu](https://img.shields.io/badge/Ubuntu_24.04_LTS-E95420?logo=ubuntu&logoColor=white)

---

## 📝 Observations & Summary

| Experiment | Strategy | Downtime | Rollback Speed | Traffic Control |
|---|---|---|---|---|
| 3 | Basic Deployment + ConfigMap | None | Medium | N/A |
| 4 | Rolling Update | Zero | Medium (undo) | Gradual (pod-by-pod) |
| 5 | Horizontal Scaling | None | Instant | Via replica count |
| 6 | Blue-Green | Zero | **Instant** (selector patch) | All-or-nothing switch |
| 7 | Canary | None | Instant (delete canary) | **Fine-grained** (replica ratio) |

> **Conclusion:** Each deployment strategy has distinct trade-offs.
> Rolling updates are the simplest default. Blue-Green provides instant rollback at the cost of double infrastructure.
> Canary offers the safest path for large-scale production releases by gradually validating changes on a small traffic slice before full promotion.
