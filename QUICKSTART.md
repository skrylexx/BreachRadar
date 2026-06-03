# QUICKSTART — BreachRadar WebUI

This guide takes you step-by-step to configure the environment and launch BreachRadar.

## Step 1: Configuration Preparation

1. **Copy the example file** to initialize your configuration:
   ```bash
   cp .env.example .env
   ```

2. **Edit the `.env` file** by adding at least this mandatory information:
   - `TARGET_DOMAIN`: Your organization's domain (e.g., `your-company.com`).
   - `UI_DB_PASSWORD`: A strong password for PostgreSQL.
   - `UI_REDIS_PASSWORD`: A strong password for Redis.
   - `UI_JWT_SECRET`: JWT encryption key (generate with `openssl rand -hex 32`).
   - `UI_ADMIN_EMAIL` & `UI_ADMIN_PASSWORD`: Credentials for the first Admin account (⚠️ MFA is disabled by default during the creation of this account to avoid blocking you. The interface will offer to activate it upon first login).

3. **Choose RansomLook mode**:
   - **Local Mode (default)**: `RANSOMLOOK_MODE=local`.
   - **SaaS Mode (hosted API)**: `RANSOMLOOK_MODE=saas` + `RANSOMLOOK_SAAS_API_KEY`.

---

## Option A: Launch with Docker (Recommended)

This method launches the entire infrastructure (PostgreSQL, Redis, Tor, Backend, Frontend) in seconds.

You have two ways to launch the project depending on your needs: **Production Mode** (real) or **Demonstration Mode** (Mocks).

### 🚀 Classic Launch (Production Mode)
This is the standard mode. BreachRadar queries real APIs with the keys you have configured.
1. Ensure `MOCK_MODE=false` in your `.env` file.
2. **Launch the full stack**:
   ```bash
   docker compose up -d
   ```

### 📸 Demonstration Launch (Mock Mode)
This mode dynamically generates fake data (critical alerts, CVEs, ransomwares, email breaches). It is **ideal for testing the interface**, making demonstrations, or taking **screenshots for LinkedIn** without exposing your real data or consuming real API quotas.
1. Open your `.env` file and set:
   ```bash
   MOCK_MODE=true
   ```
2. **Launch the full stack**:
   ```bash
   docker compose up -d
   ```
*(Note: You can also switch this mode on the fly without restarting Docker via the web interface in **Admin > Settings > Advanced**).*

---

2. **Verify status**:
   ```bash
   docker compose ps
   ```

3. **Access**:
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - Backend API: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Option B: Launch without Docker (Local Development)

Useful for modifying code and seeing changes instantly without rebuilding images.

### 1. Prerequisites
- PostgreSQL and Redis must be installed and launched locally (or via Docker for these services only).
- Python 3.12+ and Node.js 20+.

### 2. Launch the Backend
```bash
cd backend
python -m venv venv
# Activate venv (source venv/bin/activate or .\venv\Scripts\activate)
pip install -e .[dev]
uvicorn app.main:app --reload --port 8000
```

### 3. Launch the Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## Step 3: Access and First Steps

1. Log in at **[http://localhost:3000](http://localhost:3000)** with your admin credentials.
2. If you don't have API keys yet (HIBP, etc.), activate **Demonstration Mode (Mock Data)** in **Admin > Settings > Advanced**.
3. Launch your first scan from the Dashboard!

## Step 4: Validation Tests

Simulation of a GitHub event (Secret Scanning):
```bash
curl -X POST http://localhost:8000/webhooks/github \
     -H "Content-Type: application/json" \
     -H "X-GitHub-Event: secret_scanning_alert" \
     -d '{"action": "created", "repository": {"full_name": "your/repo"}, "alert": {"secret_type": "aws_access_key", "html_url": "https://github.com/your/repo/security/secret-scanning/1"}}'
```

---

## End of Tests

To cleanly shut down the Docker stack:
```bash
docker compose down
```
