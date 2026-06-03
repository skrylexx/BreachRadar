# QUICKSTART — BreachRadar WebUI

Ce guide vous accompagne pas à pas pour configurer l'environnement et lancer BreachRadar.

## Étape 1 : Préparation de la configuration

1. **Copiez le fichier d'exemple** pour initialiser votre configuration :
   ```bash
   cp .env.example .env
   ```

2. **Éditez le fichier `.env`** en ajoutant a minima ces informations obligatoires :
   - `TARGET_DOMAIN` : Le domaine de votre organisation (ex: `votre-entreprise.com`).
   - `UI_DB_PASSWORD` : Un mot de passe fort pour PostgreSQL.
   - `UI_REDIS_PASSWORD` : Un mot de passe fort pour Redis.
   - `UI_JWT_SECRET` : Clé de chiffrement JWT (générer avec `openssl rand -hex 32`).
   - `UI_ADMIN_EMAIL` & `UI_ADMIN_PASSWORD` : Identifiants du premier compte Admin (⚠️ le MFA est désactivé par défaut lors de la création de ce compte pour éviter de vous bloquer. L'interface vous proposera de l'activer à la première connexion).

3. **Choisissez le mode RansomLook** :
   - **Mode local (par défaut)** : `RANSOMLOOK_MODE=local`.
   - **Mode SaaS (API hébergée)** : `RANSOMLOOK_MODE=saas` + `RANSOMLOOK_SAAS_API_KEY`.

---

## Option A : Lancement avec Docker (Recommandé)

Cette méthode lance toute l'infrastructure (PostgreSQL, Redis, Tor, Backend, Frontend) en quelques secondes.

1. **Lancez la stack complète** :
   ```bash
   docker compose up -d
   ```

2. **Vérifiez le statut** :
   ```bash
   docker compose ps
   ```

3. **Accès** :
   - Frontend : [http://localhost:3000](http://localhost:3000)
   - Backend API : [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Option B : Lancement sans Docker (Développement local)

Utile pour modifier le code et voir les changements instantanément sans reconstruire les images.

### 1. Prérequis
- PostgreSQL et Redis doivent être installés et lancés localement (ou via Docker pour ces services uniquement).
- Python 3.12+ et Node.js 20+.

### 2. Lancer le Backend
```bash
cd backend
python -m venv venv
# Activer le venv (source venv/bin/activate ou .\venv\Scripts\activate)
pip install -e .[dev]
uvicorn app.main:app --reload --port 8000
```

### 3. Lancer le Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## Étape 3 : Accès et Premier Pas

1. Connectez-vous sur **[http://localhost:3000](http://localhost:3000)** avec vos identifiants admin.
2. Si vous n'avez pas encore de clés API (HIBP, etc.), activez le **Mode Démonstration (Mock Data)** dans **Admin > Paramètres > Avancé**.
3. Lancez votre premier scan depuis le Dashboard !

## Étape 4 : Tests de validation

Simulation d'un événement GitHub (Secret Scanning) :
```bash
curl -X POST http://localhost:8000/webhooks/github \
     -H "Content-Type: application/json" \
     -H "X-GitHub-Event: secret_scanning_alert" \
     -d '{"action": "created", "repository": {"full_name": "votre/repo"}, "alert": {"secret_type": "aws_access_key", "html_url": "https://github.com/votre/repo/security/secret-scanning/1"}}'
```

---

## Fin des tests

Pour éteindre proprement la stack Docker :
```bash
docker compose down
```

