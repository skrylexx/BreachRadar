# Mission : Refactoring Dynamique du Menu de Gauche (Sidebar)

L'objectif de cette mission est d'adapter le menu latéral pour qu'il affiche dynamiquement les pages en fonction de la configuration des clés API des différents connecteurs/outils d'OSINT.

## 📋 Spécifications Fonctionnelles

1. **Pages Disponibles par Défaut (Toujours Affichées)** :
   - Tableaux de bord (Dashboard)
   - Veille CVE
   - Renseignements (Intelligence)
   - Scans
   - Rapports
   - Alertes Ransomware
   - Profil utilisateur / Changelog
   - Pages d'administration (pour les administrateurs)

2. **Pages Outils Conditionnelles** :
   - Les pages d'outils OSINT spécifiques ([HIBP](file:///home/alex/Bureau/BreachRadar/frontend/src/app/tools/hibp/page.tsx), [GitHub](file:///home/alex/Bureau/BreachRadar/frontend/src/app/tools/github/page.tsx), [RansomLook](file:///home/alex/Bureau/BreachRadar/frontend/src/app/tools/ransomlook/page.tsx), [LeakCheck](file:///home/alex/Bureau/BreachRadar/frontend/src/app/tools/leakcheck/page.tsx), [URLScan](file:///home/alex/Bureau/BreachRadar/frontend/src/app/tools/urlscan/page.tsx), etc.) ne doivent s'afficher dans la navigation principale que si leur clé API correspondante a été configurée dans l'application.

3. **Section "Pages non connectées"** :
   - Tout outil dont la clé API **n'est pas renseignée** doit être déplacé de la navigation principale vers un sous-menu rétractable/déroulant (accordéon) situé en bas de la navigation principale.
   - Ce sous-menu s'intitulera **"Pages non connectées"** (ou équivalent traduit).
   - Cliquer sur ce sous-menu déroulera la liste des pages d'outils inactifs/non configurés afin que l'utilisateur puisse toujours y accéder s'il le souhaite (par exemple pour voir un message d'invitation à configurer la clé).

---

## 🛠️ Étapes d'Implémentation Prévues

### Étape 1 : backend — Endpoint Public de Statut des Clés API
Actuellement, l'endpoint `/api/api-keys/status` dans [api_keys.py](file:///home/alex/Bureau/BreachRadar/backend/app/routers/api_keys.py) nécessite des privilèges d'administrateur (`AdminUser`).
- **TODO** : Créer un nouvel endpoint accessible aux utilisateurs standards (ou toute personne authentifiée avec `ViewerUser`) renvoyant uniquement l'information d'activation/configuration sans exposer les clés chiffrées ou d'autres détails sensibles.
  - Exemple de route : `/api/api-keys/configured-status`
  - Exemple de réponse : `{"hibp": true, "github": false, "leakcheck": true, ...}`

### Étape 2 : frontend — Intégration de l'API & State Management
- **TODO** : Créer ou mettre à jour un service/helper API dans le frontend pour interroger ce nouvel endpoint.
- **TODO** : Mettre en cache ces informations de statut ou les charger au chargement de l'application / du layout principal pour éviter des requêtes répétées.

### Étape 3 : frontend — Refactoring de [Sidebar.tsx](file:///home/alex/Bureau/BreachRadar/frontend/src/components/layout/Sidebar.tsx)
- **TODO** : Récupérer le statut de configuration des clés API dans le composant `Sidebar`.
- **TODO** : Séparer dynamiquement la liste `NAV_ITEMS` (ou les items d'outils) en deux groupes :
  1. Les outils actifs / configurés (qui restent dans le menu principal).
  2. Les outils inactifs / non configurés.
- **TODO** : Implémenter le composant d'accordéon/collapsible pour le bloc **"Pages non connectées"** :
  - Conserver un style UI homogène avec le reste du menu (gestion du survol, icônes, états actif/inactif).
  - Gérer l'état replié/déplié (et éventuellement le sauvegarder localement via un store ou `localStorage`).

### Étape 4 : Traduction (i18n)
- **TODO** : Ajouter la chaîne de traduction pour le titre du sous-menu dans les fichiers de langue :
  - Dans [fr.json](file:///home/alex/Bureau/BreachRadar/frontend/messages/fr.json) : `"disconnectedPages": "Pages non connectées"`
  - Dans [en.json](file:///home/alex/Bureau/BreachRadar/frontend/messages/en.json) : `"disconnectedPages": "Disconnected Pages"`
