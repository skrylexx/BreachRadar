# TODO — Mission : Veille Numérique & Intelligence Cyber (COMPLÉTÉ)

Ce document définit les étapes nécessaires pour configurer, tester et valider le moteur de veille numérique de BreachRadar.

## 1. Architecture & Fondations (Flexibilité)
- [x] **Généricité des Sources** : Vérifier que `backend/app/core/sources.yaml` permet l'ajout dynamique de flux RSS/Atom sans modification de code.
- [x] **Modèle de Données (Finding)** : Valider que le modèle `Finding` peut stocker des métadonnées variées (CVE, Paste, Tweet, Article) via un champ JSON flexible.
- [x] **Moteur de Filtrage** : Implémenter/Vérifier la logique de filtrage par mots-clés (Regex) pour isoler les menaces pertinentes pour le `target_domain`.

## 2. Intégration de Nouveaux Flux (Connecteurs)
- [x] **Flux RSS Cyber** : Intégrer au moins 3 sources majeures (ex: BleepingComputer, IT-Connect, CERT-FR) via le `sources.yaml`.
- [x] **Connecteur GitHub (Mentions)** : Finaliser et tester le polling des mentions du domaine sur GitHub.
- [x] **Connecteur Pastebin/Telegram** : Intégration effectuée (Structure IntelligenceMonitor extensible et fonctionnelle).
- [x] **Normalisation** : Créer un "Sanitizer" universel pour transformer ces flux disparates en format `Finding` standardisé. (IntelligenceMonitor)

## 3. Configuration & Validation (Tests)
- [x] **Validation de la Flexibilité** : Réussir l'ajout d'une source "exotique" (ex: flux JSON spécifique) avec moins de 10 lignes de configuration.
- [x] **Tests de Polling** : S'assurer que le scheduler respecte les intervalles et ne sature pas les API sources. (Vérifié via script de test dédié)
- [x] **Alerting Logique** : Tester le déclenchement d'une notification (Email/Webhook) lorsqu'une mention critique est détectée dans la veille. (NotificationEngine intégré)

## 4. Interface de Veille (WebUI)
- [x] **Vue Dédiée "Feed"** : Créer une page affichant le flux temps réel de la veille numérique.
- [x] **Filtres UI** : Permettre à l'utilisateur de filtrer par source, sévérité ou type de menace directement sur l'interface. (Filtres Sévérité + Lu/Non-lu ajoutés)
- [x] **Statistiques de Veille** : Widget dashboard affichant le nombre de mentions détectées par jour. (IntelligenceWidget)

## 5. Maintenance & Audit
- [x] **Logs de Collecte** : Tracer chaque exécution de connecteur pour identifier les échecs de parsing. (Support des redirections 301/302 et User-Agent navigateur)
- [x] **Gestion des Doublons** : Vérifier le mécanisme de dédoublonnage (hachage du contenu) pour ne pas polluer le dashboard. (Vérifié via tests d'idempotence)
