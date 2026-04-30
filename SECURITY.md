# SECURITY.md — Procédures de Sécurité LeakMonitor

> **Document critique** — À lire avant toute manipulation de clés API.
> Révisé : 2026-04-30 | Version : 1.0

---

## Contexte de risque

Ce projet manipule des **clés API à coût réel** (certaines > 100 €/mois) et accède à des données de sécurité sensibles. Une fuite de clé API peut entraîner :

- Facturation non autorisée sur votre compte (surtout IntelX, Dehashed)
- Exposition de vos données de surveillance à un tiers
- Invalidation de vos tokens par les fournisseurs (perte d'accès immédiate)

---

## 1. Règles absolues (non négociables)

```
❌ JAMAIS de clé API dans un fichier versionné (git commit)
❌ JAMAIS de clé API dans les logs applicatifs
❌ JAMAIS de clé API dans les variables Docker exposées publiquement
❌ JAMAIS de partage de clé API par email ou messagerie non chiffrée
❌ JAMAIS de clé API dans un rapport généré

✅ Uniquement dans .env (gitignored)
✅ En production : vault (HashiCorp, AWS Secrets Manager, etc.)
✅ Une clé = un usage = un projet
```

---

## 2. Checklist avant le premier lancement

### 2.1 Vérification du .gitignore

```bash
# S'assurer que .env est bien ignoré
cat .gitignore | grep "^\.env$"
# Doit afficher : .env

# Vérifier qu'aucune clé n'est déjà suivie par git
git ls-files | grep "\.env"
# Doit retourner VIDE — si non, voir section 5.2
```

### 2.2 Vérification avant chaque commit

```bash
# Scanner le repo pour détecter des secrets potentiels
# (à lancer manuellement ou via pre-commit hook)
git diff --cached | grep -iE "(api[_-]?key|token|secret|password|passwd)\s*[:=]\s*\S+"
# Doit retourner VIDE

# Alternative avec detect-secrets (recommandé)
pip install detect-secrets
detect-secrets scan > .secrets.baseline
detect-secrets audit .secrets.baseline
```

### 2.3 Validation du .env

```bash
# Vérifier que .env existe et n'est pas vide
test -f .env && echo "OK" || echo "MANQUANT — copier .env.example"

# Vérifier que TARGET_DOMAIN est configuré
grep "^TARGET_DOMAIN=" .env | grep -v "=mondomaine.fr" | grep -v "=$"
# Doit afficher votre domaine réel

# Scanner .env pour des clés non vides
grep -E "^[A-Z_]+=.+$" .env | grep -v "^#" | wc -l
# Affiche le nombre de variables configurées
```

---

## 3. Gestion des clés API par service

### 3.1 Tableau des risques

| Service | Coût si compromis | Révocation | Monitoring |
|---|---|---|---|
| **HIBP** | ~3,50 USD/mois max | Immédiate via dashboard | Email si usage anormal |
| **GitHub Token** | 0 € (lecture seule) | Paramètres → Tokens | Log d'audit GitHub |
| **URLScan** | 0 € (gratuit) | Dashboard URLScan | — |
| **OTX AlienVault** | 0 € (gratuit) | Dashboard OTX | — |
| **LeakCheck** | ~50 USD/mois max | Dashboard LeakCheck | Alertes d'usage |
| **Dehashed** | ~180 USD/mois max | Dashboard Dehashed | Vérifier les logs |
| **IntelX** | **~500 EUR/mois** ⚠️ | Contact support | **CRITIQUE — surveiller** |
| **Shodan** | ~65 USD (one-time) | Dashboard Shodan | — |
| **Telegram** | 0 € | Révoquer session | Sessions Telegram |

> **IntelX est le service le plus risqué** financièrement. Configurer des alertes de dépenses si votre fournisseur le permet.

### 3.2 Principe de moindre privilège

Pour chaque token, accorder **uniquement les droits nécessaires** :

```
GitHub Token   → Scopes : public_repo (lecture seule UNIQUEMENT)
                 ❌ Ne pas cocher : repo, admin, write:*, delete:*

GitLab Token   → Scopes : read_api UNIQUEMENT
                 ❌ Ne pas cocher : write_repository, api (complet)

URLScan        → Permission : Search (lecture seule)
                 ❌ Ne pas cocher : Submit scans

Shodan         → API key standard (pas de droits admin)
```

---

## 4. Procédures en cas d'incident

### 4.1 Clé API suspectée compromise

```
Séquence d'urgence (< 5 minutes) :

1. RÉVOQUER la clé immédiatement (avant toute investigation)
   → Ne pas attendre de confirmer la compromission
   → Une révocation non nécessaire est moins grave qu'une clé active compromise

2. GÉNÉRER une nouvelle clé (nouveau secret, nouvelle valeur)

3. METTRE À JOUR le .env local (remplacer l'ancienne valeur)

4. VÉRIFIER les logs d'utilisation de l'ancienne clé (si le service le permet)
   → Identifier les requêtes anormales

5. NOTER l'incident : date, service, clé concernée, vecteur supposé

6. Si IntelX ou Dehashed compromis → contacter le support pour signaler
   un usage frauduleux potentiel
```

### 4.2 Secret trouvé dans un commit git

```bash
# 1. Ne pas paniquer — mais agir vite

# 2. Révoquer la clé IMMÉDIATEMENT (voir 4.1)

# 3. Nettoyer l'historique git (si repo public ou partagé)
#    ATTENTION : réécriture d'historique — coordonner avec les collaborateurs

# Option A : git filter-branch (deprecated mais universel)
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch .env' \
  --prune-empty --tag-name-filter cat -- --all

# Option B : BFG Repo Cleaner (recommandé, plus rapide)
# https://rtyley.github.io/bfg-repo-cleaner/
java -jar bfg.jar --delete-files .env

# 4. Force-push (DANGEREUX — confirmer avec l'équipe)
git push origin --force --all
git push origin --force --tags

# 5. Invalider les clones existants (GitHub : contacter le support)
```

### 4.3 Rapport généré contenant des données inattendues

```bash
# 1. Supprimer le rapport immédiatement
rm reports/<fichier_suspect>

# 2. Vérifier les autres rapports du même scan
ls -la reports/

# 3. Analyser ce qui a "filtré" en utilisant grep
grep -rE "(password|hash|[a-f0-9]{40})" reports/
# Si résultat non vide → bug critique dans le sanitizer → ouvrir une issue

# 4. Ne jamais transmettre le rapport suspect — le purger
```

---

## 5. Configuration de l'environnement de développement sécurisé

### 5.1 Pre-commit hooks (fortement recommandé)

```bash
# Installer pre-commit
pip install pre-commit

# Créer .pre-commit-config.yaml à la racine
```

Contenu du `.pre-commit-config.yaml` :

```yaml
repos:
  # Détection de secrets
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']

  # Vérification que .env n'est pas commité
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: detect-private-key      # Détecte les clés privées RSA/SSH
      - id: no-commit-to-branch
        args: ['--branch', 'main']  # Interdit les commits directs sur main

  # Linter Python
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff
      - id: ruff-format
```

```bash
# Activer les hooks
pre-commit install

# Générer la baseline des secrets (faux positifs à ignorer)
detect-secrets scan > .secrets.baseline

# Tester sur tout le repo
pre-commit run --all-files
```

### 5.2 Variables d'environnement — bonnes pratiques

```bash
# BIEN : charger les variables pour une seule session shell
export HIBP_API_KEY="votre_clé"   # Temporaire, pas dans l'historique

# ENCORE MIEUX : utiliser direnv (charge .env automatiquement)
# https://direnv.net/
# .envrc (gitignored) → direnv allow

# JAMAIS : mettre une clé dans la commande directement
uv run python -m leakmonitor scan --api-key=sk-xxx  # NON
```

### 5.3 Permissions des fichiers sensibles

```bash
# Sur Linux/macOS : restreindre les permissions du .env
chmod 600 .env
ls -la .env
# Doit afficher : -rw------- (lecture/écriture uniquement par le propriétaire)

# Vérifier régulièrement
find . -name ".env" -perm /044 -ls
# Affiche les .env lisibles par group ou others — à corriger
```

---

## 6. Tests de sécurité du code

### 6.1 Scanner le code avec Bandit

```bash
# Installer bandit (analyseur de sécurité Python)
uv add --dev bandit

# Scan complet du code source
uv run bandit -r leakmonitor/ -ll -f txt

# Rapport détaillé en HTML
uv run bandit -r leakmonitor/ -f html -o security_report.html

# Codes à surveiller particulièrement :
# B105, B106, B107 → hardcoded passwords
# B501, B502       → vérification SSL désactivée
# B603, B604       → injection shell
# B608             → injection SQL (pas de SQL ici, mais bon réflexe)
```

### 6.2 Scanner les dépendances avec Safety

```bash
# Vérifier les dépendances pour des CVE connus
pip install safety
safety check

# Via uv (exporte d'abord les requirements)
uv pip compile pyproject.toml -o /tmp/req.txt
safety check -r /tmp/req.txt
```

### 6.3 Lancer les tests de sécurité LeakMonitor

```bash
# Tests unitaires de non-régression sécurité
uv run pytest tests/test_security.py -v

# Résultats attendus :
# PASSED  test_leak_finding_has_no_sensitive_fields
# PASSED  test_report_does_not_contain_passwords
# PASSED  test_ransom_finding_portal_url_stored_but_visible
# PASSED  test_data_integrity_flags_onion_excluded
# PASSED  test_ransom_finding_elevates_global_severity_to_critical
# PASSED  test_no_ransom_no_forced_critical
# PASSED  test_empty_scan_returns_no_severity

# Tests sanitizer complets
uv run pytest tests/test_sanitizer.py -v --tb=short

# Couverture complète
uv run pytest tests/ -v --cov=leakmonitor --cov-report=term-missing
```

### 6.4 Vérification manuelle du sanitizer

```python
# Script de vérification rapide (à lancer avant chaque release)
# Sauvegarder comme scripts/verify_sanitizer.py

from leakmonitor.core.sanitizer import DataSanitizer

sanitizer = DataSanitizer()

# Cas de test critiques
test_cases = [
    ("password:abc123",                           True,  "password"),
    ("5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8",  True,  "sha1"),
    ("5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8", True, "sha256"),
    ("$2b$12$EIXZet8OhK5P9YMQjL9BreWEcEidiFuUxH6EzkyovJlbHcCy9TLWK",   True,  "bcrypt"),
    ("ghp_1234567890abcdefghij1234567890abcdef12",                        True,  "github_token"),
    ("api_key=sk-prod-xxxxxxxxxxxxx",              True,  "api_key"),
    ("alice@mondomaine.fr",                        False, "clean_email"),
    ("Adobe 2013",                                 False, "clean_breach"),
]

print("=== Vérification Sanitizer ===\n")
all_ok = True
for text, should_be_sensitive, label in test_cases:
    result = sanitizer.sanitize(text)
    is_sensitive = result.has_any_sensitive_data
    status = "✅" if is_sensitive == should_be_sensitive else "❌ ÉCHEC"
    if is_sensitive != should_be_sensitive:
        all_ok = False
    print(f"{status} [{label}] has_sensitive={is_sensitive} (attendu={should_be_sensitive})")

print(f"\n{'✅ Tous les tests passent.' if all_ok else '❌ DES TESTS ÉCHOUENT — NE PAS DÉPLOYER'}")
```

```bash
# Lancer la vérification
uv run python scripts/verify_sanitizer.py
```

---

## 7. Checklist de déploiement

Avant chaque mise en production ou partage du projet :

```
[ ] .env est dans .gitignore ET n'est pas tracké par git
[ ] git status ne montre aucun fichier sensible en staged
[ ] detect-secrets scan ne retourne aucun nouveau secret
[ ] pre-commit run --all-files passe sans erreur
[ ] uv run pytest tests/test_security.py passe à 100%
[ ] uv run bandit -r leakmonitor/ -ll ne retourne aucun HIGH
[ ] Les clés API dans .env ont les permissions minimales nécessaires
[ ] Les clés API ont une date d'expiration configurée (si le service le permet)
[ ] Un mécanisme de révocation rapide est documenté (section 4.1)
[ ] docker-compose.yml : RansomLook exposé sur 127.0.0.1 uniquement (jamais 0.0.0.0)
[ ] Aucune donnée sensible dans les rapports générés (reports/)
```

---

## 8. Rotation périodique des clés

Planifier la rotation selon le coût/risque du service :

| Service | Fréquence recommandée | Action |
|---|---|---|
| GitHub Token | Tous les 90 jours | Paramètres → Tokens → Régénérer |
| HIBP | Tous les 6 mois | Dashboard HIBP → Nouvelle clé |
| GitLab Token | Tous les 90 jours | Préférences → Tokens |
| IntelX | Tous les 3 mois ⚠️ | Support IntelX |
| Dehashed | Tous les 6 mois | Dashboard → API Key |
| LeakCheck | Tous les 6 mois | Dashboard → API |
| URLScan | Annuel | Dashboard URLScan |
| OTX | Annuel | Settings → API Key |

> Après chaque rotation : mettre à jour `.env`, relancer `uv run python -m leakmonitor sources --status` pour confirmer que tout fonctionne.

---

## 9. Isolation réseau recommandée

```bash
# Option 1 : Proxy dédié pour les requêtes OSINT
# Configurer dans .env :
HTTP_PROXY=socks5://127.0.0.1:1080
HTTPS_PROXY=socks5://127.0.0.1:1080

# Option 2 : VPN ou VPS dédié à LeakMonitor
# Avantage : les requêtes OSINT n'exposent pas votre IP réelle aux services tiers

# Option 3 (développement uniquement) : Wireguard local
# → Isole le trafic LeakMonitor du reste de la machine
```

---

## 10. Références

- [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [GitHub : Scanning for secrets](https://docs.github.com/en/code-security/secret-scanning)
- [detect-secrets](https://github.com/Yelp/detect-secrets)
- [Bandit — Python Security Linter](https://bandit.readthedocs.io)
- [ANSSI — Guide des bonnes pratiques](https://www.ssi.gouv.fr/guide/recommandations-relatives-a-lauthentification-multifacteur-et-aux-mots-de-passe/)
