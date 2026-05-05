## WebUI de BreachRadar
> Logo du site trouvable dans le dossier `images/`.

### WebUI
Exemple de designs souhaités :
- https://www.ransomlook.io/
- https://github.com
- https://www.loldrivers.io/
- https://red.flag.domains/ (pour son côté minimaliste et tech)
- https://osint.rocks/
- https://holeheosint.com/ (mais pas avec son fond qui fait mal aux yeux)
- https://uimagic.co/
- https://publicpool.co/
- https://www.digiparser.com/

#### Rappel instructions
Tu peux lire les différents fichiers, principalement `Cahier-Des-Charges_BreachRadar.md`, pour t'imprégner du projet.  
Ce dernier sert à faire du scan de leak, mais également de ransomware en cours, pour faire de la prévention, et aider les équipes de sécurité à être au courant de l'état du facteur humain de leur parc.  
Le design doit donc être accessible, orienté tech/cyber/gouvernance, ce n'est pas un outil marketing.  
Il devra être reconnaissable avec une capture d'écran de la landing page, doit se démarquer des autres sites, dont ses concurrents directs.

#### Features souhaitées
- Une interface simple, lisible
- i18n avec les langes suivantes : anglais (langue principale), français, avec un bouton pour chosir sa langue
- intégration dark mode (via switch modern avec animation, en haut de header)
- Un enregistrement (bool) des clés API renseignées
- Une base de données pour enregistrer les résultats (respect RGPD), sans enregistrer d'information sensible
- Possibilité de transmettre un rapport (.pdf) par mail en insérant l'adresse depuis le site (onglet du rapport)
- Sécurité des mots de passe renforcée (16 caractères pour les admins, 12 pour viewers)
- Intégration MFA (Authy, MobilPass ?, Microsoft Authenticator, Google Authenticator)
- Possibilité de relancer les scans depuis les pages dédiées aux outils, sinon, scan toutes les semaines (cron)
- Timestamp (sans les secondes) du dernier scan
- Une page (en bas du menu, pas hyper visible car pas ultra importante) type "CHANGELOG", ou "UPDATES", avec une traçabilité

#### Orgnisation
- Une landing page type Dashboard, avec :
  - Information sur les outils utilisables (en fonction des clés API enregistrées), avec menu déroulant pour également voir les outils non utilisables.
  - Un graphique (7j, 1 mois, 6 mois, 12 mois) montrant l'évolution du résultat des scans (type graphique NinjaOne sur l'état des machines)
  - Une page par outil avec les rapports de chaque outils disponibles
  - Une interface administrateur (compte admin créé au déploiement de la stack WebUI), permettant de créer/supprimer des utilisateurs (mail + mdp, avec reset mdp par mail, et MFA si possible), d'assigner des rôles (viewer, admin), d'ajouter ou supprimer des clés API et autre renseignements nécessaires aux outils.
  - Depuis l'interface administrateur, il y aura également une possibilité de configuration SMTP/SMTPS
  - Un bloc graphique pour un outil spécific. Il faudra sélectionner l'outil parmis ceux utilisables, et il y aura un graphique pour montrer l'évolution des scans positifs au cours du temps (durée de comparaison sélectionnable comme pour le graphique global).

### Intégration
Déploiement de la WebUI différent du lancement de la stack en cli.
Nouveau Docker type `BreachRadar_UI`, ou création d'un script permettant de lancer la web ui avec `-ui` ou de lancer la stack normale sans argument.
Intégrer tout ça dans les documents déjà existants type README.md, walkthrough...

### Technique
Le tout sera une stack "docker-compose" avec plusieurs services (app + BDD + mail)
Le BackEnd tournera sur FastAPI, et le FrontEnd NextJS + TailwindCSS + Shadcn/UI.
En ce qui concerne la Base de données, on choisir a PostgreSQL  
Authentification : JWT avec HttpOnly Cookies.  
MFA : TOTP (RFC 6238)  
Rôles : RBAC : Distinction stricte entre Admin (gestion clés/SMTP) et Viewer (consultation & export rapports).  

### Rôle viewer
Un viewer ne peut pas lancer de scan.  
Il peut :
- Voir la landing page
- Voir les rapports
- Export les rapports

### Rapports
Les rapports auront leur contenu identifiable dans le fichier `Cahier-Des-Charges_BreachRadar.md`.  
Leur format d'export sera `.pdf`.  
Il est possible d'obtenir un rapport global sur un scan complet (scans hebdomadaires), ou un rapport par outil dans l'onglet de chaque outil indépendamment.  
Possibilité de faire un rapport sur la landing page, sur le graphique d'évolution des trouvailles des scans.  
Après chaque scan hebdomadaire, il n'y a pas de rapport .pdf créé automatiquement, ce dernier devra être demandé manuellement depuis l'interface.  
Pour les transferts de rapport depuis la plateforme, il sera nécessaire de taper l'adresse de destination.

### Graphique d'évolution global
Pour le graphique d'évolution des trouvailles, voici les informations :
- batonnets
- axe X : temps
- axe Y : nombre de problématiques remontées (trouvaille pour tous les outils réunis).

### Graphique d'évolution spécifique
Pour le graphique d'évolution des trouvailles, voici les informations :
- batonnets
- axe X : temps
- axe Y : nombre de problématiques remontées pour l'outil sélectionné (à l'aide d'une petite liste déroulante, avec seulement les outils utilisables).

### Sécurité dédiée web
Protection CSRF sur les formulaires  
Rate limiting sur les endpoints de login / de relance de scan  
Logs d'accès / d'actions admin (audit trail)

### Sécurité mots de passe
, avec roration demandée par mail tous les 6 mois
- Si le mot de passe n'est pas renouvelé après 6 mois, le rendre inutilisable jusqu'à ce qu'une demande de nouveau mot de passe soit faite par l'utilisateur (envoi mail de renew)
SAUF SI MDP +24 car

### Dark mode
Pour respecter le type "Gouvernance", voici ce que je souhaite :
- Fond Principal : #09090b (Un gris-noir très profond, plus moderne que le noir pur, type Shadcn/UI).
- Surfaces (Cards/Modals) : #18181b (Pour créer du relief sans utiliser de bordures blanches agressives).
- Couleur d'Accent (The "Radar" Identity) :
  - Un Bleu Cyan/Indigo (#38bdf8) pour le côté "infrastructure sécurisée".
- Status Colors (Critique) : impérativement respecter le code couleur cyber : Rouge (CRITICAL), Orange (HIGH), Jaune (MEDIUM), Bleu/Gris (LOW).

### Fonts
- Interface (UI) : Inter.
- Données Techniques (Hashes, Emails, Logs) : JetBrains Mono.

### Mise en page
- Sidebar fine : Uniquement des icônes (Dashboard, Scans, API Keys, Users, Changelog) pour maximiser l'espace de données.
- La "Heatmap" de Risque : Au sommet du dashboard, un graphique linéaire (type NinjaOne) montrant le volume de détections sur 12 mois.  
- Cards de Statut API : Des petites cartes en haut de page indiquant le statut de tes connecteurs (HIBP: ✅, RansomLook: ✅, GitHub: ❌), avec des encadrés avec une bordure légèrement arrondie, verte ou rouge sur le côté gauche (qui dépasse un peu en haut et en bas) en fonction de l'état.  
- Tableaux de Fuites : Un design très aéré type "Stripe Dashboard", avec des badges de sévérité colorés pour scanner l'information d'un coup d'œil.

### Densité de l'information
Je veux que l'interface soit assez dense, mais pas illisible. Je souhaite un juste milieu, assez similaire visuellleement à un dashboard de monitoring SOC.

### Identité visuelle du "Radar"
Un élément graphique qui rappelle physiquement un radar (landing page discretement + au lancement des scans, en signe de chargement)

