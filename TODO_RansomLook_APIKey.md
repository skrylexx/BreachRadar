# TODO — Intégration automatique de la clé d’API RansomLook dans BreachRadar

## 1. Objectif

Mettre en place un mécanisme propre permettant à BreachRadar de **consommer automatiquement la clé d’API RansomLook** lors du déploiement de la stack Docker, sans reconfiguration manuelle dans la WebUI.

Important : l’objectif réaliste est de **propager une clé déjà obtenue et stockée (env / secret)** vers le backend BreachRadar, pas de générer une clé soi-même auprès de RansomLook (pas d’endpoint public documenté pour ça).

## 2. Contexte RansomLook — API & clé

### 2.1 Deux modes d’usage

1. **Instance auto-hébergée (Docker locale)**
   - API accessible sur `http://localhost:8888` ou via un service Docker interne (`http://ransomlook-app:8888`).
   - Dans la plupart des intégrations open source, cette instance ne nécessite **pas** de clé d’API pour les endpoints de lecture (usage défensif).

2. **Instance SaaS hébergée `https://www.ransomlook.io`**
   - RansomLook expose une API REST sur `https://www.ransomlook.io/api`.
   - La documentation indique l’utilisation d’un header `Authorization: YOUR_API_KEY` pour les requêtes (par ex. `/posts`, `/group/<name>`, `/search`).
   - La clé d’API est obtenue via le compte utilisateur RansomLook (processus manuel côté humain).

### 2.2 Conséquences pour BreachRadar

- Mode **local** : configuration actuelle (URL locale, pas de clé) reste valable.
- Mode **SaaS** : il faut prévoir :
  - une **URL d’API configurable** (ex. `RANSOMLOOK_SAAS_API_URL=https://www.ransomlook.io/api`),
  - une **clé d’API** transmise au backend (ex. `RANSOMLOOK_SAAS_API_KEY`),
  - l’ajout automatique du header `Authorization` dans le client HTTP RansomLook.

## 3. Contraintes sur l’"automatisation" de la clé

- Aucun endpoint public documenté ne permet à BreachRadar de récupérer lui-même la clé d’API RansomLook à partir du compte utilisateur.
- La seule approche viable consiste à utiliser :
  - un **secret manager** (Vault, AWS Secrets Manager, etc.),
  - ou un fichier `.env` / secret Docker,
  - injecté au moment du déploiement de la stack Docker.

**Conclusion** : “automatiser” = **brancher proprement la clé dans la stack** (via Docker / env / secrets) pour que BreachRadar l’absorbe sans intervention dans l’UI, pas générer la clé lui-même.

## 4. Stratégie technique proposée

### 4.1 Variables d’environnement à standardiser

Ajouter / formaliser les variables suivantes dans `.env.example` :

```dotenv
# RansomLook — mode d’utilisation
RANSOMLOOK_MODE=local          # local | saas

# Instance locale (Docker)
RANSOMLOOK_LOCAL_URL=http://ransomlook-app:8888

# Instance SaaS (hébergée, nécessite API key)
RANSOMLOOK_SAAS_API_URL=https://www.ransomlook.io/api
RANSOMLOOK_SAAS_API_KEY=
```

Dans la configuration Pydantic du backend :

```python
class Settings(BaseSettings):
    ransomlook_mode: Literal["local", "saas"] = "local"
    ransomlook_local_url: str = "http://ransomlook-app:8888"
    ransomlook_saas_api_url: str = "https://www.ransomlook.io/api"
    ransomlook_saas_api_key: str | None = None
```

### 4.2 Adaptation du client RansomLook dans le backend

Objectif : centraliser la logique `local` vs `saas` dans le client HTTP.

Pseudo-code :

```python
class RansomLookClient(BaseLeakClient):
    def __init__(self, settings: Settings):
        self.mode = settings.ransomlook_mode
        if self.mode == "local":
            self.base_url = settings.ransomlook_local_url.rstrip("/")
            self.headers = {}
        else:  # saas
            self.base_url = settings.ransomlook_saas_api_url.rstrip("/")
            if not settings.ransomlook_saas_api_key:
                raise RuntimeError("RANSOMLOOK_SAAS_API_KEY is required in saas mode")
            self.headers = {
                "Authorization": settings.ransomlook_saas_api_key,
            }

    @retry(...)
    async def _get(self, path: str, params: dict | None = None) -> dict | list:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base_url}{path}", params=params, headers=self.headers
            )
            response.raise_for_status()
            return response.json()
```

Les méthodes existantes (`check_health`, `check_domain`, etc.) n’ont pas besoin d’être modifiées, seules les URLs et headers changent selon le mode.

### 4.3 Intégration côté Docker

#### 4.3.1 Variantes de docker-compose

- **Mode local** (par défaut) :
  - inclut les services `ransomlook-redis`, `ransomlook-tor`, `ransomlook-app`.
  - Backend reçoit :
    - `RANSOMLOOK_MODE=local`,
    - `RANSOMLOOK_LOCAL_URL=http://ransomlook-app:8888`.

- **Mode SaaS** (sans stack RansomLook locale) :
  - ne déploie pas les conteneurs RansomLook (ou les met en `profiles` Docker).
  - Backend reçoit :
    - `RANSOMLOOK_MODE=saas`,
    - `RANSOMLOOK_SAAS_API_URL=https://www.ransomlook.io/api`,
    - `RANSOMLOOK_SAAS_API_KEY` (via env ou secret Docker).

Exemple de configuration pour le backend :

```yaml
services:
  backend:
    env_file:
      - .env
    environment:
      - RANSOMLOOK_MODE=${RANSOMLOOK_MODE:-local}
      - RANSOMLOOK_LOCAL_URL=${RANSOMLOOK_LOCAL_URL:-http://ransomlook-app:8888}
      - RANSOMLOOK_SAAS_API_URL=${RANSOMLOOK_SAAS_API_URL:-https://www.ransomlook.io/api}
      - RANSOMLOOK_SAAS_API_KEY=${RANSOMLOOK_SAAS_API_KEY:-}
```

#### 4.3.2 Gestion via secrets Docker (optionnel mais recommandé)

- Créer un fichier `ransomlook_api_key.txt` contenant la clé.
- Dans `docker-compose.yml` :

```yaml
secrets:
  ransomlook_api_key:
    file: ./secrets/ransomlook_api_key.txt

services:
  backend:
    secrets:
      - ransomlook_api_key
    environment:
      - RANSOMLOOK_MODE=saas
      - RANSOMLOOK_SAAS_API_URL=https://www.ransomlook.io/api
```

- Script d’entrée simplifié :

```bash
#!/usr/bin/env bash
set -euo pipefail

if [ "${RANSOMLOOK_MODE:-local}" = "saas" ] && [ -f "/run/secrets/ransomlook_api_key" ]; then
  export RANSOMLOOK_SAAS_API_KEY="$(cat /run/secrets/ransomlook_api_key)"
fi

exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Ainsi, au déploiement, dès que la stack Docker est montée avec le secret, le backend récupère automatiquement la clé et la met à disposition du client RansomLook.

### 4.4 Propagation dans la WebUI (lecture seule)

- Dans la page Admin > Clés API, pour RansomLook :
  - afficher le mode courant (`local` / `saas`),
  - afficher un bool “clé présente” (mais jamais la valeur),
  - permettre de basculer le mode (avec garde-fous et documentation).

- Aucun formulaire Web ne doit afficher ou renvoyer la clé vers le frontend.

## 5. Plan de travail détaillé

1. **Backend**
   - [ ] Ajouter les nouvelles variables dans les Settings (Pydantic).
   - [ ] Adapter `RansomLookClient` pour gérer les modes `local` / `saas`.
   - [ ] Ajouter des tests unitaires :
     - [ ] `test_saas_mode_requires_api_key`
     - [ ] `test_local_mode_ignores_api_key`
     - [ ] `test_headers_set_in_saas_mode`.

2. **Docker**
   - [ ] Mettre à jour `docker-compose.yml` pour distinguer RansomLook local (services inclus) et SaaS (services optionnels).
   - [ ] Ajouter un exemple d’usage de secrets Docker pour la clé.
   - [ ] Mettre à jour `.env.example` avec les nouvelles variables.

3. **WebUI (Admin)**
   - [ ] Exposer le mode courant RansomLook (local/saas).
   - [ ] Afficher un bool “clé présente / non présente”.
   - [ ] Ajouter un formulaire de bascule de mode (écriture côté backend, pas de lecture de la clé).

4. **Documentation**
   - [ ] Mettre à jour `README.md` pour expliquer les deux modes.
   - [ ] Ajouter une section “RansomLook SaaS Integration” avec un exemple d’appel API :

```python
import requests

API = "https://www.ransomlook.io/api"
HEADERS = {"Authorization": "YOUR_API_KEY"}
resp = requests.get(f"{API}/search", params={"query": "acme"}, headers=HEADERS)
```

   - [ ] Préciser clairement que la clé est obtenue depuis le compte RansomLook et qu’il n’existe pas d’endpoint automatique de génération pour BreachRadar.

## 6. Points d’attention / risques

- Mauvaise gestion des modes pourrait :
  - envoyer des requêtes locales sans clé vers l’API SaaS (erreur 401/403),
  - ou exposer une clé d’API inutilement si l’instance locale ne la requiert pas.

- Le mécanisme de secrets doit être testé en conditions réelles (Docker local, puis CI/CD) pour vérifier :
  - que la clé est bien lue au démarrage,
  - qu’elle n’apparaît nulle part dans les logs ou dans l’UI.

- Bien documenter que :
  - mode recommandé par défaut : RansomLook local, gratuit, sans clé ;
  - mode SaaS : utile si l’on ne souhaite pas maintenir la stack Docker RansomLook, mais implique confiance dans un service externe et la gestion stricte de la clé API.
