# Commands Executed — DevOps Lab 1

> Chronological record of all commands run during this lab.
> Environment: Ubuntu 24.04 LTS

---

## 1. System Update & Tool Installation

```bash
# Update package lists
sudo apt update && sudo apt upgrade -y

# Install Git
sudo apt install -y git
git --version
# git version 2.43.0

# Install Node.js 20 (via NodeSource)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
node --version   # v20.x.x
npm --version    # 10.x.x

# Install Docker
sudo apt install -y ca-certificates curl gnupg lsb-release
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io
sudo usermod -aG docker $USER   # add current user to docker group
docker --version
# Docker version 26.x.x

# Install Jenkins
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key \
  | sudo tee /usr/share/keyrings/jenkins-keyring.asc > /dev/null
echo "deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
  https://pkg.jenkins.io/debian-stable binary/" \
  | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null
sudo apt update
sudo apt install -y jenkins
sudo systemctl enable jenkins
sudo systemctl start jenkins
sudo systemctl status jenkins
# Jenkins running on http://localhost:8080

# Get Jenkins initial admin password
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

---

## 2. Git Configuration

```bash
# Set global identity
git config --global user.name  "Your Name"
git config --global user.email "your@email.com"
git config --global init.defaultBranch main

# Verify configuration
git config --list
```

---

## 3. Repository Setup

```bash
# Initialize local repository
cd ~
mkdir devops-lab1 && cd devops-lab1
git init
git remote add origin https://github.com/<your-username>/devops-lab1.git

# Initial commit
git add .
git commit -m "feat: initial project structure with Node.js app and Jenkinsfile"
git push -u origin main
```

---

## 4. Running the App Locally

```bash
cd app
npm install
npm start
# Server running at http://localhost:3000

# Test endpoints
curl http://localhost:3000/
curl http://localhost:3000/health
curl http://localhost:3000/info
```

---

## 5. Running Tests

```bash
cd app
npm test
# PASS  test/app.test.js
# Test Suites: 1 passed, 1 total
# Tests:       5 passed, 5 total
# Coverage: >90%
```

---

## 6. Running Lint

```bash
cd app
npm run lint
# No lint errors found
```

---

## 7. Docker Operations

```bash
# Build the image
docker build -t devops-lab1-app:latest .

# Run the container
docker run -d --name devops-lab1-app -p 3000:3000 devops-lab1-app:latest

# Verify container is running
docker ps

# Check container logs
docker logs devops-lab1-app

# Health check
curl http://localhost:3000/health

# Stop and remove container
docker stop devops-lab1-app
docker rm devops-lab1-app
```

---

## 8. Jenkins Pipeline

```bash
# Check Jenkins service status
sudo systemctl status jenkins

# View Jenkins logs
sudo journalctl -u jenkins -f

# Trigger pipeline via CLI (optional)
java -jar jenkins-cli.jar -s http://localhost:8080/ build devops-lab1 --wait
```

---

## 9. Git Commit History

```bash
# View commit log
git log --oneline --graph --all

# Sample commits:
# a1b2c3d feat: add Node.js Express app with health endpoints
# d4e5f6g feat: add Jenkinsfile with 7-stage CI/CD pipeline
# g7h8i9j feat: add Dockerfile with health check
# j0k1l2m feat: add GitHub Actions CI workflow
# m3n4o5p docs: add README, COMMANDS, PIPELINE_STAGES, SETUP guides
# p6q7r8s chore: add .gitignore and ESLint configuration
```
