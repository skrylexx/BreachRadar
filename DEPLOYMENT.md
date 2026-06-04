# Deployment Guide — BreachRadar

This guide provides instructions for deploying **BreachRadar** in a production environment (VPS, Dedicated Server, Cloud).

---

## 1. Prerequisites

### Infrastructure
- **Server**: A VPS or Cloud instance with at least **2 vCPUs** and **4GB RAM**.
- **OS**: Ubuntu 22.04 LTS or 24.04 LTS (recommended).
- **Domain**: A public domain or sub-domain (e.g., `breachradar.example.com`) pointed to your server's IP via an **A record**.
- **Ports**: 80 (HTTP) and 443 (HTTPS) must be open in your firewall (UFW/Cloud Security Groups).

### Software
- **Docker Engine**: v24.0 or higher.
- **Docker Compose**: v2.20 or higher.

---

## 2. Server Preparation (Hardening)

Before deploying the application, secure your server.

### Firewall Configuration (UFW)
```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Install Docker
Follow the [official Docker installation guide for Ubuntu](https://docs.docker.com/engine/install/ubuntu/).

---

## 3. Deployment Steps

### 1. Clone the Repository
```bash
git clone https://github.com/skrylexx/BreachRadar.git /opt/breachradar
cd /opt/breachradar
```

### 2. Configure Environment
```bash
cp .env.example .env
nano .env
```

**Mandatory Production Settings:**
- `MOCK_MODE=false`
- `UI_DB_PASSWORD`: Use a complex random string.
- `UI_REDIS_PASSWORD`: Use a complex random string.
- `UI_JWT_SECRET`: Generate with `openssl rand -hex 32`.
- `UI_ADMIN_EMAIL`: Your professional email.
- `UI_ADMIN_PASSWORD`: Use a strong temporary password (you will change it).

### 3. Launch the Stack
```bash
docker compose up -d
```

---

## 4. Reverse Proxy & SSL (Nginx)

We recommend using **Nginx** as a reverse proxy to handle SSL termination.

### 1. Install Nginx and Certbot
```bash
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx
```

### 2. Configure Nginx
Create a new configuration file:
```bash
sudo nano /etc/nginx/sites-available/breachradar
```

**Configuration Template:**
```nginx
server {
    listen 80;
    server_name breachradar.example.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # API Proxy (handled by Next.js if using internal rewrites, 
    # but direct backend access can be proxied here if needed)
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3. Enable Configuration & SSL
```bash
sudo ln -s /etc/nginx/sites-available/breachradar /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
sudo certbot --nginx -d breachradar.example.com
```

---

## 5. Persistence & Backups

### Docker Volumes
By default, `docker-compose.yml` uses named volumes for database persistence:
- `db_data`: PostgreSQL data.
- `redis_data`: Redis persistence.

### Database Backups
Schedule a daily cron job to dump the database:
```bash
#!/bin/bash
BACKUP_DIR="/opt/breachradar/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
docker exec breachradar-db pg_dump -U postgres breachradar > $BACKUP_DIR/db_$TIMESTAMP.sql
find $BACKUP_DIR -type f -mtime +30 -delete
```

---

## 6. Maintenance & Updates

### Updating BreachRadar
```bash
cd /opt/breachradar
git pull origin main
docker compose pull
docker compose up -d --remove-orphans
```

### Viewing Logs
```bash
docker compose logs -f api
docker compose logs -f ui
```

---

## 7. Security Best Practices

1. **MFA**: Activate Multi-Factor Authentication immediately after the first login.
2. **API Keys**: Use a dedicated service account/API key for HaveIBeenPwned and other sources.
3. **Database**: Never expose the database port (5432) to the public internet.
4. **Secrets**: Use Docker Secrets or a Vault if you have high security requirements.
