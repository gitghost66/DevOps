# Lab 3: Monitoring, Logging & DevSecOps

## Overview

Design an automated, observable, and secure infrastructure workflow. This lab demonstrates:
- Infrastructure provisioning and configuration using **Ansible** and **Terraform**
- Monitoring and centralized logging using **Prometheus**, **Grafana**, and the **ELK Stack**
- Security and quality practices: pipeline security scanning, feature flags, load testing, and automated browser testing

---

## Folder Structure

```
lab3/
├── ansible/                    # Ansible playbooks & roles
│   ├── inventory/              # Host inventory files
│   ├── playbooks/              # Main playbooks
│   └── roles/                  # Reusable roles (common, prometheus, grafana, elk)
├── terraform/                  # Infrastructure-as-Code (IaC)
├── monitoring/                 # Prometheus + Grafana configs
│   ├── prometheus/             # Scrape configs & alert rules
│   └── grafana/                # Dashboards & datasources
├── elk/                        # ELK Stack configuration
│   ├── elasticsearch/
│   ├── logstash/
│   └── kibana/
├── security/                   # DevSecOps configurations
│   └── .github/workflows/      # CI/CD security scanning pipeline
├── feature-flags/              # Feature flag definitions
├── load-testing/               # Locust & k6 load test scripts
└── selenium/                   # Automated browser tests
```

---

## Components

### 1. Ansible – Configuration Management
- `ansible/playbooks/site.yml` – Master playbook
- `ansible/playbooks/monitoring.yml` – Deploys Prometheus & Grafana
- `ansible/playbooks/elk-stack.yml` – Deploys ELK stack
- `ansible/roles/` – Reusable roles for each service

### 2. Terraform – Infrastructure Provisioning
- `terraform/main.tf` – Defines VMs, networking, and services
- `terraform/variables.tf` – Input variables
- `terraform/outputs.tf` – Exported outputs

### 3. Monitoring – Prometheus & Grafana
- `monitoring/prometheus/prometheus.yml` – Scrape configurations
- `monitoring/prometheus/alert_rules.yml` – Alerting rules
- `monitoring/grafana/dashboards/` – Pre-built dashboards
- `monitoring/docker-compose.yml` – Spin up the monitoring stack

### 4. ELK Stack – Centralized Logging
- `elk/elasticsearch/elasticsearch.yml` – ES configuration
- `elk/logstash/logstash.conf` – Log pipeline
- `elk/kibana/kibana.yml` – Kibana configuration
- `elk/docker-compose.yml` – Spin up ELK stack

### 5. Security – DevSecOps
- `.github/workflows/security-scan.yml` – Trivy + SonarQube CI pipeline
- `security/sonarqube/sonar-project.properties` – SonarQube config

### 6. Feature Flags
- `feature-flags/features.json` – Feature flag definitions

### 7. Load Testing
- `load-testing/locustfile.py` – Locust load test
- `load-testing/k6-script.js` – k6 load test script

### 8. Selenium – Automated Browser Testing
- `selenium/tests/test_ui.py` – Selenium UI test suite

---

## Quick Start

### Start Monitoring Stack
```bash
cd monitoring
docker-compose up -d
# Prometheus: http://localhost:9090
# Grafana:    http://localhost:3000 (admin/admin)
```

### Start ELK Stack
```bash
cd elk
docker-compose up -d
# Elasticsearch: http://localhost:9200
# Kibana:        http://localhost:5601
```

### Run Ansible Playbooks
```bash
cd ansible
ansible-playbook -i inventory/hosts.ini playbooks/site.yml
```

### Apply Terraform
```bash
cd terraform
terraform init
terraform plan
terraform apply
```

### Run Load Tests
```bash
# Locust
cd load-testing
locust -f locustfile.py --headless -u 100 -r 10 --run-time 60s --host http://localhost:8080

# k6
k6 run load-testing/k6-script.js
```

### Run Selenium Tests
```bash
cd selenium
pip install -r requirements.txt
pytest tests/test_ui.py -v
```
