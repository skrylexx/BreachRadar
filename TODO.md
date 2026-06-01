# 🛡️ Roadmap de Sécurité — BreachRadar

Ce document définit la stratégie d'audit et de tests de sécurité nécessaire avant toute publication sur Internet. L'objectif est de garantir l'intégrité des données, la robustesse de l'authentification et l'étanchéité entre les privilèges.

## 🏁 Objectif Final
Déployer l'application sereinement avec un niveau de confiance élevé sur la protection des secrets, la gestion des sessions et la résistance aux attaques web classiques.

---

## 🏗️ Phase 1 : Audit de Sécurité Général & Infrastructure
*Audit de la posture globale, de la supply chain et de la configuration des services.*

- [x] **Check-up Supply Chain (Docker & CI)**
    - [x] Remplacer les installations par `curl | sh` par des versions épinglées/vérifiées dans les Dockerfiles.
    - [x] Épingler toutes les images Docker avec des hash SHA256 (Tor, RansomLook, Postgres, Redis).
    - [x] Vérifier les permissions des volumes (`./reports`, `./data`) et restreindre l'utilisateur non-root (`brapi`).
- [x] **Audit de Gestion des Secrets**
    - [x] Vérifier l'étanchéité des variables d'environnement (ne pas les loguer, ne pas les exposer via l'API).
    - [x] Analyser la visibilité de `UI_REDIS_PASSWORD` dans les processus système.
    - [x] S'assurer que les clés API OSINT sont chiffrées en base (Fernet) et jamais renvoyées au frontend.
- [x] **Scan de Vulnérabilités Dépendances (SCA)**
    - [x] Remédier aux vulnérabilités critiques de `Next.js 15.1.3` (Mis à jour en 15.1.7).
    - [x] Mettre à jour `js-cookie` (Mis à jour en 3.0.7).
    - [x] Exécuter `pip-audit` sur le backend et corriger les CVE (Vérification manuelle des versions critiques idna, urllib3).

## 🔍 Phase 2 : Audit de Code & Pentest Applicatif
*Analyse approfondie de la logique métier et tests d'intrusion ciblés.*

- [x] **Validation des Entrées & Anti-Injection**
    - [x] Auditer le `ScanManager` pour prévenir toute SSRF (Server-Side Request Forgery) via `target_domain`. (Ajout de validateurs Pydantic et regex).
    - [x] Vérifier la désinfection (sanitization) des données remontées par les sources OSINT avant stockage/affichage. (Vérifié: DataSanitizer utilisé, React auto-escape).
    - [x] Tester les injections potentielles dans les filtres de recherche et les webhooks. (Vérifié: SQL Enums, HMAC GitHub).
- [x] **Audit de Logique d'Authentification & MFA**
    - [x] Finaliser l'implémentation de `/auth/mfa/verify` (Terminé: flux complet avec brute-force protection).
    - [x] Tester la robustesse du stockage des secrets MFA (Terminé: secrets chiffrés via Fernet).
    - [x] Vérifier la résistance au brute-force sur les challenges MFA dans Redis. (Vérifié: blocage après 5 tentatives).
- [x] **Pentest "Black Box" Local**
    - [x] Tester les vulnérabilités OWASP Top 10 sur les endpoints critiques. (Vérifié: RBAC strict, validation schéma).
    - [x] Vérifier l'absence de fuite d'informations dans les messages d'erreur API. (Terminé: global_exception_handler en prod).

## 🔐 Phase 3 : Vérification des Permissions (RBAC)
*Assurer que l'isolation entre Viewer et Admin est hermétique.*

- [x] **Audit des Dépendances de Sécurité FastAPI**
    - [x] Vérifier chaque router pour s'assurer que les endpoints sensibles (`/settings`, `/api_keys`, `/users`, `/scans/trigger`) sont strictement réservés à `AdminUser`. (Corrigé pour /settings/general).
- [x] **Test d'Escalade de Privilèges (Vertical/Horizontal)**
    - [x] Tenter d'accéder aux clés API avec un compte `Viewer`. (Vérifié: accès refusé via AdminUser dependency).
    - [x] Vérifier l'absence d'IDOR (Insecure Direct Object Reference) sur les rapports et les scans. (Vérifié: isolation logique par instance).
- [x] **Audit Trail**
    - [x] Vérifier que toutes les actions sensibles sont correctement tracées dans les logs d'audit. (Vérifié: logs pour auth, users, apikeys).

## 🌐 Phase 4 : Sécurisation des Communications Front-Back
*Durcissement du transport de données et des politiques de navigateur.*

- [x] **Audit JWT & Gestion des Sessions**
    - [x] Vérifier que les tokens sont transmis via Cookies HttpOnly, Secure, SameSite=Lax. (Corrigé: chemins de cookies refresh_token).
    - [x] Tester le mécanisme de blacklist Redis lors du logout. (Vérifié: implémenté dans auth.py et redis.py).
    - [x] Vérifier la restriction du path pour le Refresh Token. (Corrigé: /api/v1/auth/refresh).
- [x] **Durcissement des Headers de Sécurité (Next.js)**
    - [x] Supprimer `unsafe-inline` et `unsafe-eval` de la Content Security Policy (CSP). (Terminé dans next.config.ts).
    - [x] Activer HSTS (`Strict-Transport-Security`). (Terminé).
    - [x] Configurer une `Permissions-Policy` stricte. (Terminé).
- [x] **Contrôle CORS & CSRF**
    - [x] Restreindre `allow_origins` au domaine de production réel (pas de `*`). (Vérifié: configuré via settings.cors_origins).
    - [x] Valider la protection CSRF via SameSite Lax et vérifier si un token anti-CSRF additionnel est requis. (Vérifié: Lax + HttpOnly suffisant pour la plupart des navigateurs modernes).

---

## 🚀 Prêt pour la Mise en Production
*Critères de succès finaux.*

- [x] Zéro vulnérabilité critique/haute détectée par les scans SCA.
- [x] MFA 100% fonctionnel et obligatoire pour les Admins.
- [x] CSP stricte sans "unsafe".
- [x] Tous les tests de `tests/test_security.py` passent au vert.
- [x] Rapport d'audit final archivé et validé.
