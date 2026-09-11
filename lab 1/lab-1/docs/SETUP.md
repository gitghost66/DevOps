# Jenkins & Environment Setup Guide — DevOps Lab 1

> Step-by-step instructions to configure Jenkins and connect it to the GitHub repository.
> Environment: Ubuntu 24.04 LTS

---

## 1. Jenkins Installation

```bash
# Add Jenkins GPG key and repository
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key \
  | sudo tee /usr/share/keyrings/jenkins-keyring.asc > /dev/null

echo "deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] \
  https://pkg.jenkins.io/debian-stable binary/" \
  | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null

sudo apt update
sudo apt install -y jenkins

# Start and enable on boot
sudo systemctl enable --now jenkins
sudo systemctl status jenkins
```

Jenkins will be accessible at: **http://localhost:8080**

---

## 2. Initial Jenkins Setup

1. Get the initial admin password:
   ```bash
   sudo cat /var/lib/jenkins/secrets/initialAdminPassword
   ```
2. Open **http://localhost:8080** in a browser
3. Paste the password and click **Continue**
4. Choose **Install suggested plugins**
5. Create the first admin user
6. Set Jenkins URL to `http://localhost:8080/`

---

## 3. Required Jenkins Plugins

Install these additional plugins via **Manage Jenkins → Plugins → Available plugins**:

| Plugin | Purpose |
|---|---|
| **Pipeline** | Enables Declarative Pipeline / Jenkinsfile |
| **Git** | GitHub integration |
| **GitHub Integration** | Webhook support for auto-triggering |
| **Docker Pipeline** | Docker commands in pipeline steps |
| **NodeJS** | Manages Node.js installations |
| **Blue Ocean** (optional) | Modern pipeline visualization |

---

## 4. Configure Node.js in Jenkins

1. Go to **Manage Jenkins → Tools**
2. Scroll to **NodeJS installations** → click **Add NodeJS**
3. Name: `NodeJS-20`
4. Version: `NodeJS 20.x`
5. Click **Save**

---

## 5. Create the Pipeline Job

1. Click **+ New Item**
2. Name: `devops-lab1`
3. Type: **Pipeline** → click **OK**
4. Under **Pipeline**:
   - Definition: **Pipeline script from SCM**
   - SCM: **Git**
   - Repository URL: `https://github.com/<your-username>/devops-lab1.git`
   - Branch: `*/main`
   - Script Path: `Jenkinsfile`
5. Click **Save**

---

## 6. Configure GitHub Webhook (Auto-trigger)

1. In your GitHub repo: **Settings → Webhooks → Add webhook**
2. Payload URL: `http://<your-jenkins-ip>:8080/github-webhook/`
3. Content type: `application/json`
4. Events: **Just the push event**
5. Click **Add webhook**

Now every `git push` will automatically trigger the Jenkins pipeline.

---

## 7. Run the Pipeline Manually

1. Open the `devops-lab1` job in Jenkins
2. Click **Build Now**
3. Click the build number → **Console Output** to watch it live
4. All 7 stages should show **green ✓**

---

## 8. Docker Setup for Jenkins

Allow Jenkins to run Docker commands:

```bash
# Add jenkins user to the docker group
sudo usermod -aG docker jenkins

# Restart Jenkins to apply
sudo systemctl restart jenkins

# Verify
sudo -u jenkins docker ps
```
