> Ceci est un document permettant de stocker le prompt à utiliser en cas de changement d'IA.
> Il n'est pas à prendre en compte par les IA, et doit être ignoré.

#### PROMPT
```
Voici l'état actuel de mon projet. Lis le README.md pour comprendre l'architecture et le ROADMAP.md pour savoir où Claude s'est arrêté. Reprends la suite en respectant le même protocole de documentation.
```

#### PROMPT ORIGINE
```
# MISSION
En te basant sur le cahier des charges fourni, lance la phase de construction du projet. Ton objectif est de poser des bases solides, modulaires et parfaitement documentées pour permettre une collaboration fluide entre IA (Claude/Gemini) et humain.

# LIVRABLES ATTENDUS (Phase 1)
1. **README.md** : Un fichier complet incluant :
   - Présentation du projet et architecture technique.
   - Instructions d'installation et de lancement.
   - Arborescence actuelle du projet.
2. **ROADMAP.md** : Un journal de bord structuré comprenant :
   - La vision globale des étapes à venir.
   - Une section **CHANGELOG** listant précisément chaque modification effectuée durant cette itération.
   - Un indicateur d'avancement (ex: [██░░░] 40%).
3. **CODE** : Les premiers fichiers sources fonctionnels selon les priorités du cahier des charges.

# PROTOCOLE DE GESTION DES TOKENS & SÉCURITÉ
- **Arrêt Préventif** : Avant d'atteindre la limite de ta fenêtre de contexte ou de génération (environ 80% de ta capacité), arrête d'écrire du code. 
- **Dernière Action** : Consacre tes derniers tokens à mettre à jour le fichier `ROADMAP.md` pour résumer exactement où tu t'es arrêté, ce qui reste à faire, et les points de vigilance pour l'IA qui prendra la relève.
- **Interopérabilité** : Utilise des commentaires explicites et une structure standardisée pour que Gemini puisse reprendre le travail sans perte d'information.

# INSTRUCTIONS DE STYLE
- Précision technique maximale.
- Code propre, commenté et modulaire.
- Pas de blabla inutile : concentre-toi sur l'exécution et le suivi visuel de l'avancée.

Tu peux maintenant commencer l'implémentation.
```