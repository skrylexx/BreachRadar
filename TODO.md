# Ce qui a été fait (État actuel)

- **Veille Numérique (Cyber Intel)** : Le filtrage restrictif basé sur le nom de domaine cible a été supprimé dans `IntelligenceMonitor`. Désormais, toutes les actualités RSS provenant des flux configurés (ex: The Hacker News, Dark Reading, CERT-FR, DevOps, InfoQ, IT-Connect) sont ingérées en base et disponibles pour la lecture/formation. 191 articles ont été ajoutés en base manuellement lors du test.
- **Filtres Technologiques CVE** : Un nouveau champ "Technologies à surveiller" a été ajouté dans l'interface `Paramètres > CVE` (sous la forme d'un champ texte séparé par des virgules). Ce paramètre est sauvegardé dans `SystemSettings` (clé `cve_tech_filters`) et est utilisé par `CVEMonitor` pour filtrer dynamiquement les alertes CVE issues de NVD, OSV, GitHub Advisories et CVEFeed, limitant ainsi le volume (over flood) aux seules technos de l'utilisateur (ex: "Windows, Debian, VEEAM").
- **UI & Expérience** : Les listes de vulnérabilités CVE et de Cyber Intel utilisent désormais les données à jour et un bouton "Actions" a été ajouté pour commenter / taguer sur les CVE. Des animations de chargement ont été ajoutées sur les boutons d'actualisation.
- **Scripts de test** : Des scripts temporaires ont été utilisés pour tester l'ingestion puis supprimés.

---

# 📋 Ce qu'il reste à faire / tester

1. **Test visuel de l'onglet Cyber Intel** :
   - [ ] Vérifier que les articles issus du RSS (The Hacker News, etc.) remontent bien en nombre dans l'onglet "Veille / Intelligence" de l'interface graphique. (Note : s'assurer de bien tester en réactualisant la page car le chargement asynchrone a pu être décalé de la première tentative).
   
2. **Test du Filtre Technologique CVE** :
   - [ ] Dans l'interface d'administration, entrer une liste spécifique (ex: `VEEAM, Proxmox`).
   - [ ] Déclencher un nouveau scan ou attendre le polling automatique.
   - [ ] Confirmer que les nouvelles entrées CVE remontées ne concernent *que* les technos ciblées.

3. **Vérification du Polling au Démarrage (Scheduler Lock)** :
   - [ ] Analyser le mécanisme de `ScanScheduler` (`backend/app/main.py`) et son verrou Redis (`breachradar:scheduler_lock`). Parfois, un redémarrage sauvage du container API maintient le verrou actif trop longtemps, ce qui bloque le polling immédiat au démarrage.
   - [ ] Trouver une solution pour libérer le verrou proprement lors d'un `docker compose down` ou adapter le délai d'expiration pour s'assurer que la veille se lance toujours de manière fiable après un déploiement.

4. **Test de l'ajout de Commentaires / Tags (CVE)** :
   - [ ] Tester de bout en bout l'action "Commenter / Taguer" ajoutée dans le tableau CVE (`frontend/src/app/(dashboard)/alerts/cve/client.tsx`).
   - [ ] S'assurer que le commentaire est bien persisté en base de données et restitué lors du rechargement de la page.
