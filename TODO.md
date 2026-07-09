# Ce qui a été fait (État actuel)

- **Veille Numérique (Cyber Intel)** : Le filtrage restrictif basé sur le nom de domaine cible a été supprimé dans `IntelligenceMonitor`. Désormais, toutes les actualités RSS provenant des flux configurés (ex: The Hacker News, Dark Reading, CERT-FR, DevOps, InfoQ, IT-Connect) sont ingérées en base et disponibles pour la lecture/formation. 191 articles ont été ajoutés en base manuellement lors du test.
- **Filtres Technologiques CVE** : Un nouveau champ "Technologies à surveiller" a été ajouté dans l'interface `Paramètres > CVE` (sous la forme d'un champ texte séparé par des virgules). Ce paramètre est sauvegardé dans `SystemSettings` (clé `cve_tech_filters`) et est utilisé par `CVEMonitor` pour filtrer dynamiquement les alertes CVE issues de NVD, OSV, GitHub Advisories et CVEFeed, limitant ainsi le volume (over flood) aux seules technos de l'utilisateur (ex: "Windows, Debian, VEEAM").
- **UI & Expérience** : Les listes de vulnérabilités CVE et de Cyber Intel utilisent désormais les données à jour et un bouton "Actions" a été ajouté pour commenter / taguer sur les CVE. Des animations de chargement ont été ajoutées sur les boutons d'actualisation.
- **Scripts de test** : Des scripts temporaires ont été utilisés pour tester l'ingestion puis supprimés.
- **Polling au Démarrage (Scheduler Lock)** : Le mécanisme de `ScanScheduler` dans `backend/app/main.py` a été corrigé. Le verrou Redis (`breachradar:scheduler_lock`) est désormais correctement libéré lors de l'arrêt du service, évitant ainsi de bloquer le polling après un redémarrage.
- **Ajout de Commentaires / Tags (CVE)** : L'action de commenter / taguer a été entièrement implémentée (Backend & Frontend) via `frontend/src/app/(dashboard)/alerts/cve/client.tsx`, l'API (`cveApi`) et la base de données. Les commentaires sont persistés et affichés correctement.

---

# 📋 Ce qu'il reste à faire / tester

1. **Test visuel de l'onglet Cyber Intel** :
   - [ ] Vérifier que les articles issus du RSS (The Hacker News, etc.) remontent bien en nombre dans l'onglet "Veille / Intelligence" de l'interface graphique. (Note : s'assurer de bien tester en réactualisant la page car le chargement asynchrone a pu être décalé de la première tentative).
   
2. **Test du Filtre Technologique CVE** :
   - [ ] Dans l'interface d'administration, entrer une liste spécifique (ex: `VEEAM, Proxmox`).
   - [ ] Déclencher un nouveau scan ou attendre le polling automatique.
   - [ ] Confirmer que les nouvelles entrées CVE remontées ne concernent *que* les technos ciblées.
