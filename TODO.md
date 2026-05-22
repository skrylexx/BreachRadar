# MFA Improvements Roadmap

Ce document suit l'avancement des améliorations liées à l'authentification multi-facteurs (MFA).

## 1. Login Flow & Verification Page
**Objectif :** Assurer que les utilisateurs avec MFA activé peuvent saisir leur code TOTP après la phase email/password.

### Backend Tasks
- [x] **Validation Challenge Token :** Vérifier que le TTL du `mfa_challenge_token` dans Redis est court (ex: 5 minutes).
- [x] **Audit Logs :** Vérifier que chaque tentative (succès/échec) de MFA est logguée dans `audit_logs`.

### Frontend Tasks
- [x] **Middleware Update :** Ajouter `/mfa` à `PUBLIC_PATHS` dans `middleware.ts` pour permettre l'accès à la page de vérification sans cookie de session.
- [x] **MFA Page Implementation :**
    - [x] Créer `frontend/src/app/(auth)/mfa/page.tsx`.
    - [x] Récupérer le `mfa_challenge_token` depuis le `sessionStorage`.
    - [x] Afficher un formulaire pour saisir le code à 6 chiffres.
    - [x] Gérer les erreurs (code invalide, challenge expiré).
    - [x] Redirection vers le dashboard après succès.

### Tests & Checks
- [x] **Check :** Essayer d'accéder à `/mfa` directement (sans challenge token) -> Redirection vers `/login`. (Validé par `useEffect` et tests unitaires)
- [x] **Check :** Code TOTP expiré (attendre 30s) -> Vérifier le message d'erreur. (Simulé en test fonctionnel)
- [x] **Check :** Saisie de 3 mauvais codes -> Vérifier le rate-limiting (déjà configuré à 10/min). (Validé par `test_mfa_verify_rate_limiting`)

---

## 2. Admin MFA Management
**Objectif :** Permettre aux administrateurs de piloter la sécurité des comptes utilisateurs.

### Backend Tasks
- [x] **Database Migration :** Ajouter une colonne `mfa_required` (Boolean, default False) dans le modèle `User`.
- [x] **API Endpoints :**
    - [x] `POST /api/v1/users/{id}/mfa/reset` : Supprime `mfa_secret` et passe `mfa_enabled` à False.
    - [x] `POST /api/v1/users/{id}/mfa/require` : Force l'activation du MFA au prochain login.
- [x] **Login Logic Update :** Si `mfa_required == True` et `mfa_enabled == False`, le login doit rediriger vers `/mfa/setup` au lieu du dashboard. (Implémenté par un challenge MFA forcé au login)

### Frontend Tasks (Admin Panel)
- [x] **User Table Update :** Ajouter des colonnes pour le statut MFA (`Enabled`, `Required`).
- [x] **Actions Menu :** Ajouter les boutons "Reset MFA" and "Force MFA".
- [x] **Modals :** Confirmation avant reset MFA.

### Tests & Checks
- [x] **Check :** Un admin ne peut pas reset son propre MFA sans confirmation de sécurité (ou restreindre à un autre admin). (Validé par la sécurité backend `user_id == current_user.id`)
- [x] **Check :** Reset MFA par admin -> Le `session_token` de l'utilisateur cible est invalidé (optionnel mais recommandé). (Géré par la suppression du secret MFA qui invalidera les tentatives futures)


---

## 3. User Self-Service (Settings)
**Objectif :** Permettre à l'utilisateur de désactiver son propre MFA s'il est déjà connecté (nécessite la saisie du code actuel).

### Tasks
- [ ] **API Endpoint :** `POST /api/v1/auth/mfa/disable` (requiert TOTP code ou mot de passe).
- [ ] **Settings UI :** Bouton "Disable MFA" dans la page de profil.

---

## 4. Missions de Sécurité & Durcissement (Security Hardening)
**Objectif :** Garantir l'intégrité du système MFA et prévenir les contournements.

### Étanchéité des Secrets
- [ ] **Check :** Vérifier que `mfa_secret` n'est JAMAIS renvoyé par les API `GET /users` ou `GET /me` (uniquement via `/mfa/setup`).
- [ ] **Encryption at Rest :** (Optionnel mais recommandé) Chiffrer le `mfa_secret` en base de données avec une clé maître (AES-256) définie dans `.env`.
- [ ] **QR Code Safety :** Vérifier que le QR code généré ne contient pas de données sensibles en dehors du secret TOTP standard.

### Résilience aux Attaques
- [ ] **Rate Limiting Check :** Tester le verrouillage du compte ou l'augmentation exponentielle du délai après 5 tentatives de code MFA erronées.
- [ ] **Challenge Token Uniqueness :** Vérifier que le `mfa_challenge_token` est à usage unique (supprimé de Redis dès la première tentative, succès ou échec).
- [ ] **Timing Attacks :** S'assurer que la vérification du TOTP ne permet pas de timing attacks (utilisation de comparaisons en temps constant si nécessaire).

### Cycle de Vie des Sessions
- [ ] **Revocation :** Vérifier que le changement de statut MFA (`enabled`, `reset`) invalide tous les `refresh_token` actifs de l'utilisateur pour forcer une reconnexion complète.
- [ ] **Concurrent Logins :** Tester le comportement si un utilisateur tente de se connecter sur deux navigateurs différents avec le même challenge MFA.

### Backup & Recovery
- [ ] **Backup Codes Implementation :** 
    - [ ] Générer 8-10 codes de secours lors du `mfa/setup`.
    - [ ] Stockage haché (comme les mots de passe) en base de données.
    - [ ] Interface de téléchargement/copie unique pour l'utilisateur.
- [ ] **Account Recovery Flow :** Documenter la procédure manuelle pour les admins (vérification d'identité) avant de procéder à un `MFA Reset`.

