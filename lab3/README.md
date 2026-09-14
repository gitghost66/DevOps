# Lab 3: Monitoring, Logging & DevSecOps

> **Course:** DevOps | **Lab:** 3 of 3
>
> Design an automated, observable, and secure infrastructure workflow using industry-standard tools across provisioning, monitoring, logging, security, and testing.

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Folder Structure](#folder-structure)
4. [Components](#components)
   - [Ansible – Configuration Management](#1-ansible--configuration-management)
   - [Terraform – Infrastructure Provisioning](#2-terraform--infrastructure-provisioning)
   - [Monitoring – Prometheus & Grafana](#3-monitoring--prometheus--grafana)
   - [ELK Stack – Centralized Logging](#4-elk-stack--centralized-logging)
   - [Security – DevSecOps Pipeline](#5-security--devsecops-pipeline)
   - [Feature Flags](#6-feature-flags)
   - [Load Testing](#7-load-testing)
   - [Selenium – Browser Testing](#8-selenium--automated-browser-testing)
5. [Quick Start](#quick-start)
6. [Service Endpoints](#service-endpoints)
7. [Tools & Versions](#tools--versions)

---

## Overview

| Area | Tools Used |
|---|---|
| **Infrastructure Provisioning** | Terraform (AWS VPC, EC2, SGs) |
| **Configuration Management** | Ansible playbooks & roles |
| **Monitoring** | Prometheus, Grafana, Alertmanager, Node Exporter, cAdvisor |
| **Centralized Logging** | Elasticsearch, Logstash, Kibana, Filebeat (ELK 8.x) |
| **Security Scanning** | Trivy, Gitleaks, SonarQube, OWASP ZAP |
| **Feature Flags** | JSON-based flag store with rollout percentages |
| **Load Testing** | Locust (Python), k6 (JavaScript) |
| **Browser Testing** | Selenium WebDriver + pytest |

---

## Prerequisites

| Tool | Version | Install |
|---|---|---|
| Docker & Docker Compose | ≥ 24.x | [docs.docker.com](https://docs.docker.com/get-docker/) |
| Terraform | ≥ 1.7.0 | [developer.hashicorp.com](https://developer.hashicorp.com/terraform/install) |
| Ansible | ≥ 2.16 | `pip install ansible` |
| Python | ≥ 3.11 | [python.org](https://www.python.org/downloads/) |
| k6 | ≥ 0.50 | [k6.io/docs](https://k6.io/docs/get-started/installation/) |
| Google Chrome | Latest | Required for Selenium |

> **Note:** All monitoring and ELK services run via Docker Compose — no local installation needed beyond Docker.

---

## Folder Structure

```
lab3/
├── README.md
│
├── ansible/                              # Configuration Management
│   ├── ansible.cfg                       # Global Ansible settings
│   ├── inventory/
│   │   └── hosts.ini                     # Server inventory (monitoring, elk, app)
│   ├── playbooks/
│   │   ├── site.yml                      # Master playbook (runs all roles)
│   │   ├── monitoring.yml                # Deploy Prometheus + Grafana
│   │   ├── elk-stack.yml                 # Deploy ELK Stack
│   │   └── security.yml                  # Run security scans (Trivy, Gitleaks)
│   └── roles/
│       ├── common/tasks/main.yml         # Base packages, sysctl tuning
│       ├── prometheus/
│       │   ├── tasks/main.yml            # Install & configure Prometheus
│       │   └── templates/prometheus.yml.j2  # Dynamic scrape config (Jinja2)
│       ├── grafana/tasks/main.yml        # Install Grafana + datasource provisioning
│       └── elk/tasks/main.yml            # Deploy ELK via Docker
│
├── terraform/                            # Infrastructure as Code (AWS)
│   ├── main.tf                           # VPC, subnets, SGs, EC2 instances
│   ├── variables.tf                      # Input variable definitions
│   ├── outputs.tf                        # Exported IPs and service URLs
│   └── terraform.tfvars                  # Variable values (edit before applying)
│
├── monitoring/                           # Prometheus + Grafana Stack
│   ├── docker-compose.yml                # Prometheus, Grafana, Alertmanager, Node Exporter, cAdvisor
│   ├── prometheus/
│   │   ├── prometheus.yml                # Scrape job configurations
│   │   └── alert_rules.yml               # Alerting rules (CPU, memory, disk, app, ES)
│   └── grafana/
│       ├── datasources/prometheus.yml    # Auto-provisioned Prometheus datasource
│       └── dashboards/                   # Dashboard JSON files (add here)
│
├── elk/                                  # ELK Stack (Elasticsearch-Logstash-Kibana)
│   ├── docker-compose.yml                # ES, Logstash, Kibana, Filebeat
│   ├── elasticsearch/
│   │   └── elasticsearch.yml             # Cluster & node configuration
│   ├── logstash/
│   │   ├── logstash.conf                 # Input → Filter (Grok/GeoIP) → Output pipeline
│   │   └── pipelines.yml                 # Pipeline worker configuration
│   └── kibana/
│       └── kibana.yml                    # Kibana server & ES connection settings
│
├── security/                             # DevSecOps
│   ├── .github/workflows/
│   │   └── security-scan.yml             # CI pipeline: Trivy + Gitleaks + SonarQube + ZAP
│   └── sonarqube/
│       └── sonar-project.properties      # SonarQube SAST project configuration
│
├── feature-flags/
│   └── features.json                     # Feature flags with rollout % and config
│
├── load-testing/
│   ├── locustfile.py                     # Locust: multi-class users, event hooks
│   └── k6-script.js                      # k6: staged ramp-up, SLO thresholds, custom metrics
│
└── selenium/
    ├── requirements.txt                  # Python dependencies
    └── tests/
        └── test_ui.py                    # Selenium suite: homepage, login, responsive, perf
```

---

## Components

### 1. Ansible – Configuration Management

Ansible automates server configuration across all hosts defined in the inventory.

**Playbooks:**

| Playbook | Purpose |
|---|---|
| `site.yml` | Master playbook – runs all roles across all host groups |
| `monitoring.yml` | Installs Docker, deploys Prometheus + Grafana stack |
| `elk-stack.yml` | Deploys ELK Stack, sets `vm.max_map_count`, waits for health |
| `security.yml` | Runs Trivy image scan, Gitleaks, OWASP dependency check |

**Roles:**

| Role | What it does |
|---|---|
| `common` | Installs base packages, tunes sysctl, sets timezone |
| `prometheus` | Downloads Prometheus binary, creates systemd service, deploys config from Jinja2 template |
| `grafana` | Adds Grafana APT repo, installs plugins, provisions Prometheus datasource |
| `elk` | Sets kernel parameters, deploys ELK via Docker Compose |

```bash
# Run the full playbook
ansible-playbook -i ansible/inventory/hosts.ini ansible/playbooks/site.yml

# Run a specific playbook
ansible-playbook -i ansible/inventory/hosts.ini ansible/playbooks/monitoring.yml

# Dry-run (check mode)
ansible-playbook -i ansible/inventory/hosts.ini ansible/playbooks/site.yml --check
```

---

### 2. Terraform – Infrastructure Provisioning

Provisions AWS infrastructure: VPC, public subnet, internet gateway, security groups, and EC2 instances for each service tier.

**Resources created:**

| Resource | Details |
|---|---|
| VPC | `10.0.0.0/16` with DNS enabled |
| Public Subnet | `10.0.1.0/24` |
| Security Groups | `monitoring-sg`, `elk-sg`, `app-sg` with scoped ingress rules |
| EC2 – Monitoring | `t3.medium` – runs Prometheus + Grafana |
| EC2 – ELK | `t3.large` – runs Elasticsearch, Logstash, Kibana |
| EC2 – App | `t3.small` × 2 – application servers |

```bash
cd terraform

# 1. Edit terraform.tfvars with your values
# 2. Initialize
terraform init

# 3. Review the plan
terraform plan

# 4. Apply
terraform apply

# 5. View outputs (IPs and service URLs)
terraform output

# 6. Destroy when done
terraform destroy
```

---

### 3. Monitoring – Prometheus & Grafana

A full observability stack deployed via Docker Compose.

**Services:**

| Service | Port | Purpose |
|---|---|---|
| Prometheus | `9090` | Metrics collection & storage |
| Grafana | `3000` | Dashboards & visualization |
| Alertmanager | `9093` | Alert routing & notifications |
| Node Exporter | `9100` | Host system metrics (CPU, RAM, disk) |
| cAdvisor | `8888` | Container resource metrics |

**Alert Rules (`alert_rules.yml`):**

| Alert | Threshold | Severity |
|---|---|---|
| `HighCPUUsage` | CPU > 80% for 5m | warning |
| `CriticalCPUUsage` | CPU > 95% for 2m | critical |
| `HighMemoryUsage` | Memory > 85% for 5m | warning |
| `DiskSpaceLow` | Disk < 15% free | warning |
| `DiskSpaceCritical` | Disk < 5% free | critical |
| `InstanceDown` | Target unreachable for 1m | critical |
| `HighHTTPErrorRate` | 5xx rate > 5% | warning |
| `ElasticsearchClusterRed` | Cluster status RED | critical |

```bash
cd monitoring
docker-compose up -d

# Check status
docker-compose ps

# Reload Prometheus config without restart
curl -X POST http://localhost:9090/-/reload
```

---

### 4. ELK Stack – Centralized Logging

Centralized log ingestion, processing, and visualization.

**Services:**

| Service | Port | Purpose |
|---|---|---|
| Elasticsearch | `9200` | Log storage & search engine |
| Logstash | `5044` | Log pipeline (Beats input) |
| Logstash | `5000` | Syslog input |
| Kibana | `5601` | Log visualization & search UI |
| Filebeat | — | Ships container logs to Logstash |

**Logstash Pipeline (`logstash.conf`):**
- **Input:** Filebeat (port 5044), Syslog (port 5000), TCP JSON (port 5001)
- **Filter:** Grok parsing for Nginx/Apache logs, GeoIP enrichment, date normalization, health check log dropping
- **Output:** Elasticsearch with daily rolling indices (`logstash-YYYY.MM.dd`)

```bash
cd elk
docker-compose up -d

# Check Elasticsearch health
curl http://localhost:9200/_cluster/health?pretty

# List indices
curl http://localhost:9200/_cat/indices?v

# Check Logstash pipeline status
curl http://localhost:9600/_node/stats/pipelines?pretty
```

---

### 5. Security – DevSecOps Pipeline

GitHub Actions pipeline runs on every push and daily at 2 AM UTC.

**Scans:**

| Job | Tool | What it checks |
|---|---|---|
| `trivy-scan` | Trivy | Docker image – CVEs (CRITICAL, HIGH) |
| `trivy-fs-scan` | Trivy | Filesystem + Terraform IaC misconfigurations |
| `gitleaks` | Gitleaks | Secrets & credentials in git history |
| `sonarqube` | SonarQube | SAST – code quality & security hotspots |
| `dependency-audit` | Safety / pip-audit | Python dependency vulnerabilities |
| `owasp-zap` | OWASP ZAP | DAST – live application security scan |

> **Required GitHub Secrets:** `SONAR_TOKEN`, `SONAR_HOST_URL`

```bash
# Run Trivy locally against a Docker image
trivy image --severity CRITICAL,HIGH myapp:latest

# Run Trivy against Terraform configs
trivy config ./terraform

# Scan for secrets with Gitleaks
docker run --rm -v $(pwd):/repo zricethezav/gitleaks detect --source=/repo
```

---

### 6. Feature Flags

JSON-based feature flags control the rollout of features without redeployment.

**Defined flags (`features.json`):**

| Flag | Status | Rollout |
|---|---|---|
| `new_dashboard` | ✅ enabled | 100% |
| `elk_logging` | ✅ enabled | 100% |
| `prometheus_metrics` | ✅ enabled | 100% |
| `rate_limiting` | ✅ enabled | 100% |
| `dark_mode` | ⚠️ beta | 20% |
| `canary_deployment` | ❌ disabled | 0% |
| `load_testing_mode` | ❌ disabled | 0% |

To enable a flag, set `"enabled": true` and `"rolloutPercentage": 100` in `feature-flags/features.json`.

---

### 7. Load Testing

Two load testing tools are provided for comprehensive performance validation.

#### Locust (`locustfile.py`)

- **User classes:** `SpikeUser` (normal think time) + `HeavyUser` (aggressive)
- **Tasks:** homepage, dashboard, item listing, item creation, health check
- **Hooks:** `on_test_start` / `on_test_stop` for reporting

```bash
pip install locust

# Headless (CI mode)
locust -f load-testing/locustfile.py \
  --headless -u 100 -r 10 --run-time 60s \
  --host http://localhost:8080

# Web UI (interactive)
locust -f load-testing/locustfile.py --host http://localhost:8080
# Open: http://localhost:8089
```

#### k6 (`k6-script.js`)

- **Stages:** Warm-up → 50 VUs → spike to 100 VUs → ramp-down
- **SLO Thresholds:** P95 < 2s, error rate < 5%, TTFB < 1s
- **Custom metrics:** `error_rate`, `login_latency`, `api_latency`, `page_views`

```bash
# Basic run
k6 run load-testing/k6-script.js

# Custom VUs and duration
k6 run --vus 50 --duration 60s load-testing/k6-script.js

# Export results to JSON
k6 run --out json=results.json load-testing/k6-script.js

# Against a different host
BASE_URL=http://myapp.example.com k6 run load-testing/k6-script.js
```

---

### 8. Selenium – Automated Browser Testing

pytest-based Selenium suite with Chrome WebDriver.

**Test classes:**

| Class | Tests |
|---|---|
| `TestHomePage` | Page loads, header present, load time < 3s |
| `TestNavigation` | Dashboard link, back navigation |
| `TestLoginFlow` | Login page, form elements, invalid/valid login |
| `TestResponsiveDesign` | Desktop, Laptop, Tablet, Mobile viewports |
| `TestAPIEndpoints` | `/health` and `/metrics` endpoints |
| `TestPerformance` | Navigation Timing API – load time, TTFB |

```bash
cd selenium

# Install dependencies
pip install -r requirements.txt

# Run all tests (headless)
pytest tests/test_ui.py -v

# Run with HTML report
pytest tests/test_ui.py -v --html=report.html

# Run specific test class
pytest tests/test_ui.py::TestLoginFlow -v

# Run against a custom host
APP_URL=http://myapp.example.com pytest tests/test_ui.py -v

# Run in headed mode (show browser)
HEADLESS=false pytest tests/test_ui.py -v

# Run tests in parallel (4 workers)
pytest tests/test_ui.py -v -n 4
```

---

## Quick Start

```bash
# 1. Clone and enter lab3
cd lab3

# 2. Start Monitoring Stack
cd monitoring && docker-compose up -d && cd ..

# 3. Start ELK Stack
cd elk && docker-compose up -d && cd ..

# 4. (Optional) Provision AWS infrastructure
cd terraform
terraform init && terraform plan && terraform apply
cd ..

# 5. (Optional) Run Ansible against provisioned servers
ansible-playbook -i ansible/inventory/hosts.ini ansible/playbooks/site.yml

# 6. Run load tests
locust -f load-testing/locustfile.py --headless -u 50 -r 5 --run-time 30s --host http://localhost:8080
k6 run load-testing/k6-script.js

# 7. Run browser tests
cd selenium && pip install -r requirements.txt
pytest tests/test_ui.py -v
```

---

## Service Endpoints

| Service | URL | Credentials |
|---|---|---|
| Prometheus | http://localhost:9090 | — |
| Grafana | http://localhost:3000 | `admin` / `admin` |
| Alertmanager | http://localhost:9093 | — |
| Elasticsearch | http://localhost:9200 | — |
| Kibana | http://localhost:5601 | — |
| Logstash API | http://localhost:9600 | — |
| Node Exporter | http://localhost:9100/metrics | — |
| cAdvisor | http://localhost:8888 | — |
| Locust Web UI | http://localhost:8089 | — |

---

## Tools & Versions

| Tool | Version |
|---|---|
| Prometheus | v2.51.0 |
| Grafana | 10.4.2 |
| Alertmanager | v0.27.0 |
| Node Exporter | v1.7.0 |
| cAdvisor | v0.49.1 |
| Elasticsearch | 8.13.0 |
| Logstash | 8.13.0 |
| Kibana | 8.13.0 |
| Filebeat | 8.13.0 |
| Terraform | ≥ 1.7.0 |
| Ansible | ≥ 2.16 |
| Trivy | 0.50.1 |
| Locust | latest |
| k6 | ≥ 0.50 |
| Selenium | 4.18.1 |
