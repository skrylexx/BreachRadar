# QUICKSTART — BreachRadar WebUI

Ce guide vous accompagne pas à pas pour configurer l'environnement et lancer l'infrastructure via Docker de la nouvelle plateforme BreachRadar orientée WebUI.

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
   - `UI_ADMIN_EMAIL` & `UI_ADMIN_PASSWORD` : Identifiants du premier compte Admin.

3. **Choisissez le mode RansomLook** :

   - **Mode local (par défaut)** :
     - Laissez `RANSOMLOOK_MODE=local`.
     - Vérifiez que `RANSOMLOOK_LOCAL_URL=http://ransomlook-app:8888`.
   - **Mode SaaS (API hébergée)** :
     - Modifiez dans `.env` :
       - `RANSOMLOOK_MODE=saas`
       - `RANSOMLOOK_SAAS_API_URL=https://www.ransomlook.io/api`
       - `RANSOMLOOK_SAAS_API_KEY=<clé API obtenue dans votre compte RansomLook>`

   Les termes de recherche peuvent être enrichis avec :
   - `RANSOMLOOK_SEARCH_TERMS` : liste de noms commerciaux / filiales, séparés par des virgules.

## Étape 2 : Lancement de la Stack Docker unifiée

Nous avons unifié l'intégralité de l'infrastructure WebUI, l'API Backend et les composants OSINT dans le `docker-compose.yml`.

1. **Lancez la stack complète** en arrière-plan :
   ```bash
   docker compose up -d
   ```

2. **Vérifiez que les services démarrent correctement** :
   ```bash
   docker compose ps
   ```
   Vous devriez voir `breachradar-postgres`, `breachradar-ui-redis`, `breachradar-api`, `breachradar-ui`, ainsi que la stack `ransomlook` avec le statut `Up` en mode local (ou uniquement les services BreachRadar si vous êtes en mode SaaS).

## Étape 3 : Accès à la plateforme

1. Ouvrez votre navigateur web et rendez-vous sur **[http://localhost:3000](http://localhost:3000)**.
2. Connectez-vous avec les identifiants `UI_ADMIN_EMAIL` et `UI_ADMIN_PASSWORD` configurés.
3. L'interface principale vous donne désormais accès à la surveillance continue de votre domaine, à la configuration des sources, et à l'historique des alertes (Ransomware, Secret Scanning, etc).

## Étape 4 : Tests manuels de validation

### Test A : Le webhook GitHub
L'API écoute désormais sur l'endpoint `/webhooks/github` pour intercepter les événements (ex. Secret Scanning). 
Simulation avec curl :
```bash
curl -X POST http://localhost:8000/webhooks/github \
     -H "Content-Type: application/json" \
     -H "X-GitHub-Event: secret_scanning_alert" \
     -d '{"action": "created", "repository": {"full_name": "votre/repo"}, "alert": {"secret_type": "aws_access_key", "html_url": "https://github.com/votre/repo/security/secret-scanning/1"}}'
```

### Test B : L'alerte critique Ransomware
RansomLook est scruté en continu par l'orchestrateur. Surveillez les logs si besoin :
```bash
# Logs du backend FastAPI (Orchestrateur)
docker compose logs -f breachradar-api

# Logs du scraper RansomLook (mode local uniquement)
docker compose logs -f ransomlook-app
```

## Fin des tests

Une fois vos tests validés, vous pouvez éteindre proprement la stack :
```bash
docker compose down
```
