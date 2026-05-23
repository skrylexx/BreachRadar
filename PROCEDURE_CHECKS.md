# Procédure de Vérification des Versions & Sécurité

Ce document détaille les étapes manuelles et automatisées pour vérifier l'intégrité et la fraîcheur de la stack technologique de BreachRadar.

## 📅 Fréquence recommandée : 1 fois par mois ou à chaque nouvelle phase majeure.

---

### 1. Backend (Python / FastAPI)

#### A. Inventaire des dépendances
```bash
cd backend
pip list --format=columns
```

#### B. Scan de vulnérabilités (SCA)
*Utiliser pip-audit (recommandé) ou safety.*
```bash
pip-audit
# ou
safety check
```

#### C. Vérification du Dockerfile
- Vérifier la version de l'image de base (`python:3.12-slim`).
- Consulter [Docker Hub](https://hub.docker.com/_/python) pour les vulnérabilités de l'image.

---

### 2. Frontend (Node.js / Next.js)

#### A. Scan de vulnérabilités intégré
```bash
cd frontend
npm audit
```

#### B. Vérification des versions obsolètes
```bash
npm outdated
```

#### C. Audit des Images Docker
- Vérifier la version de `node:20-alpine` dans le Dockerfile frontend.

---

### 3. Services & Infrastructure

#### A. PostgreSQL
Vérifier la version majeure dans `docker-compose.yml` (actuellement `16-alpine`) et comparer avec les notes de version de PostgreSQL.

#### B. Redis
Vérifier la version `7-alpine` et s'assurer qu'aucune CVE critique n'affecte les fonctionnalités utilisées (MFA, Blacklist).

---

### 4. Protocole de Mise à Jour (Step-by-Step)

1. **Sauvegarde** : Créer une branche `security/update-YYYY-MM-DD`.
2. **Mise à jour isolée** : Mettre à jour une dépendance à la fois.
3. **Tests de non-régression** :
   - Backend : `pytest`
   - Frontend : `npm run build`
4. **Validation Docker** : `docker-compose up --build`
5. **Documentation** : Mettre à jour `TECH_STACK.md` et `ROADMAP.md`.
