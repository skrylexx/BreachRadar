# BreachRadar — Frontend WebUI

Ce dossier contient l'interface utilisateur de BreachRadar, construite avec Next.js.

## 🚀 Technologies utilisées

- **Framework** : [Next.js 15](https://nextjs.org/) (App Router)
- **Langage** : [TypeScript](https://www.typescriptlang.org/)
- **Styling** : [Tailwind CSS](https://tailwindcss.com/)
- **Composants** : [Shadcn UI](https://ui.shadcn.com/) (basé sur Radix UI)
- **Graphiques** : [Recharts](https://recharts.org/)
- **Gestion de formulaires** : React Hook Form & [Zod](https://zod.dev/)
- **Internationalisation** : [next-intl](https://next-intl-docs.vercel.app/) (Français / Anglais)
- **Gestion d'état** : [Zustand](https://github.com/pmndrs/zustand)

## 🛠️ Utilités du Frontend

1. **Dashboard de surveillance** : Visualisation globale de l'état de sécurité du domaine.
2. **Gestion des alertes** : Interface pour consulter les fuites de données, les ransomwares et les CVE.
3. **Administration** : Gestion des utilisateurs, des clés API et des paramètres du système.
4. **Visualisation OSINT** : Pages dédiées pour chaque outil de veille (RansomLook, CVE, etc.).
5. **Reporting** : Interface de consultation et de téléchargement des rapports générés par le backend.

## 💻 Installation locale (sans Docker)

Si vous souhaitez lancer le frontend nativement pour le développement :

### 1. Prérequis
- Node.js 20+ installé.
- npm ou pnpm.
- Le backend BreachRadar doit être accessible (généralement sur `http://localhost:8000`).

### 2. Setup de l'environnement
```bash
# Se placer dans le dossier frontend
cd frontend

# Installer les dépendances
npm install
```

### 3. Configuration
Le frontend utilise le fichier `.env` situé à la racine du projet (`../.env`).
Assurez-vous que `NEXT_PUBLIC_API_URL` est correctement défini (ex: `http://localhost:8000`).

### 4. Lancement
```bash
# Lancer le serveur de développement avec Turbopack
npm run dev
```
L'interface sera accessible sur [http://localhost:3000](http://localhost:3000).

## 🧪 Qualité & Build
```bash
# Vérification du typage TypeScript
npm run type-check

# Linting
npm run lint

# Build de production
npm run build
```
