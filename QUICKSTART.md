# QUICKSTART — BreachRadar

Ce guide va vous accompagner pas à pas pour configurer l'environnement, lancer l'infrastructure via Docker et valider que l'ensemble des modules (Orchestrateur, Scheduler, Webhook, RansomLook) fonctionnent correctement.

## Étape 1 : Préparation de la configuration

1. **Copiez le fichier d'exemple** pour initialiser votre configuration sécurisée :
   ```bash
   cp .env.example .env
   ```

2. **Éditez le fichier `.env`** avec vos clés API (Optionnel mais recommandé pour avoir des données réelles) :
   - `TARGET_DOMAIN` : Le domaine de votre organisation (ex: `votre-entreprise.com`).
   - `HIBP_API_KEY` : Clé de l'API HaveIBeenPwned.
   - `GITHUB_TOKEN` : Token GitHub classique (sans scopes particuliers) pour la recherche.
   - `HUNTER_API_KEY` : Si vous avez un compte Hunter.io pour le résolveur d'emails.
   - Configurez les options SMTP (`SMTP_SERVER`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`) si vous souhaitez tester la réception d'emails en cas d'Alerte Ransomware Critique.

3. **Activez le Scheduler** :
   Dans le fichier `.env`, assurez-vous que `SCHEDULE_ENABLED=True` pour tester le planificateur asynchrone (vous pouvez régler le cron `SCHEDULE_CRON="*/5 * * * *"` pour un test rapide toutes les 5 minutes).

## Étape 2 : Lancement de la Stack Docker unifiée

Nous avons unifié l'intégralité de l'infrastructure dans le fichier `docker-compose.yml`. Cela inclut l'application principale, le moteur de webhook, RansomLook, Redis et Tor.

1. Lancez la commande suivante à la racine du projet :
   ```bash
   docker-compose up --build -d
   ```
   *(Le flag `-d` lance les conteneurs en arrière-plan. Retirez-le si vous souhaitez voir les logs s'afficher en direct dans votre terminal).*

2. Vérifiez que les 4 conteneurs tournent correctement :
   ```bash
   docker-compose ps
   ```
   Vous devriez voir `breachradar`, `ransomlook-app`, `ransomlook-redis`, et `ransomlook-tor` avec le statut `Up`. Les `healthchecks` vont passer au vert (`healthy`) au bout de quelques secondes.

## Étape 3 : Tests manuels de validation

Maintenant que l'application tourne en arrière-plan (en mode `schedule`), vous pouvez valider son fonctionnement par plusieurs moyens.

### Test A : Le Scan manuel
Si vous souhaitez déclencher un scan unique pour tester l'orchestrateur immédiatement, utilisez la commande `scan` en exécutant l'outil depuis le conteneur principal :
```bash
docker-compose exec breachradar python -m breachradar scan
```
👉 Observez la console : L'outil devrait valider le domaine, résoudre les emails (theHarvester + Hunter), et interroger les APIs en respectant le rate-limit.
👉 Vérifiez la génération du rapport dans le dossier partagé `./reports/`. Le `report.html` ou le `report.pdf` devrait être magnifiquement formaté avec le nouveau dashboard.

### Test B : Le serveur Webhook GitHub
Le conteneur BreachRadar écoute par défaut sur le port `8080` pour intercepter les Webhooks GitHub (Secret Scanning ou Push Events).
Vous pouvez simuler l'envoi d'une alerte avec un utilitaire comme `curl` :
```bash
curl -X POST http://localhost:8080/webhook/github \
     -H "Content-Type: application/json" \
     -H "X-GitHub-Event: secret_scanning_alert" \
     -d '{"action": "created", "repository": {"full_name": "votre/repo"}, "alert": {"secret_type": "aws_access_key", "html_url": "https://github.com/votre/repo/security/secret-scanning/1"}}'
```
👉 Regardez les logs de BreachRadar : `docker-compose logs -f breachradar`
Vous devriez voir l'interception de la requête, le log de l'alerte (`[🚨 ALERTE GITHUB]`), et si vous avez configuré un Webhook Discord/Slack, l'alerte y sera poussée instantanément.

### Test C : L'alerte critique Ransomware (RansomLook)
Le moteur RansomwareTracker est prioritaire. Si le `TARGET_DOMAIN` configuré dans `.env` fait partie des victimes recensées par RansomLook, le rapport global passera automatiquement en sévérité `CRITICAL` et une notification d'extorsion sera envoyée par Email/Webhook dès les premières secondes du scan.

## Étape 4 : Inspection des logs

En cas de comportement inattendu, les logs de l'application sont votre meilleur atout :
```bash
# Voir les logs en direct du moniteur de fuites et du webhook
docker-compose logs -f breachradar

# Voir les logs du scraper RansomLook (si les données mettent du temps à apparaître)
docker-compose logs -f ransomlook-app
```

## Fin des tests

Une fois vos tests validés, vous pouvez éteindre proprement la stack :
```bash
docker-compose down
```

Vous êtes maintenant prêt pour attaquer la **Phase 5 (Hardening)** en toute sérénité.
