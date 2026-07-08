# How to Retrieve a GitHub Personal Access Token (PAT) / Comment récupérer un jeton d'accès personnel GitHub (PAT)

[English Version](#english-version) | [Version Française](#version-française)

---

## English Version

This guide explains how to generate a GitHub Personal Access Token (PAT) to authenticate the BreachRadar search engine. 

Using a token increases the GitHub Search API rate limit from **60 requests/hour** (unauthenticated) to **5,000 requests/hour** (authenticated).

### 🛡️ Security Best Practices (Least Privilege)
To protect your GitHub account, always grant the minimum necessary permissions:
*   **For Public Repositories (Recommended):** If you are only monitoring public repositories, generate a token with **no scopes/permissions checked**. This creates a secure, read-only token.
*   **For Private Repositories:** Only grant read permissions to private repositories if you specifically need BreachRadar to monitor code within your private or organizational repositories.
*   **Never** check administrative (`admin`), write (`write:*`), or delete (`delete:*`) permissions.

---

### Method 1: Fine-grained Personal Access Tokens (Recommended)
Fine-grained tokens are GitHub's modern security standard, offering granular control.

1.  Log in to your GitHub account and go to [github.com](https://github.com).
2.  In the upper-right corner, click your profile photo, then click **Settings**.
3.  In the left sidebar, scroll to the bottom and click **Developer settings**.
4.  In the left sidebar, under **Personal access tokens**, click **Fine-grained tokens**.
5.  Click **Generate new token**.
6.  Configure the token settings:
    *   **Token name:** Enter a descriptive name (e.g., `BreachRadar-Code-Search`).
    *   **Expiration:** Select an expiration period (e.g., 30, 60, or 90 days).
    *   **Description:** (Optional) Describe the purpose.
    *   **Resource owner:** Select your account (or organization).
7.  Under **Repository access**:
    *   Select **Public repositories (read-only)** if you only monitor public code.
    *   Select **All repositories** or **Only select repositories** if you need to monitor private repositories.
8.  Under **Permissions** -> **Repository permissions**:
    *   **Metadata:** Ensure it is set to **Read-only** (usually required and automatically enabled).
    *   **Contents:** Set to **Read-only** (only required if monitoring private repositories).
    *   Leave all other permissions set to **No access**.
9.  Click **Generate token**.
10. Copy the generated token immediately. **It will not be displayed again.**

---

### Method 2: Personal Access Tokens (Classic)
Classic tokens are the older format, useful if fine-grained tokens face compatibility issues.

1.  Go to **Settings** > **Developer settings** > **Personal access tokens** > **Tokens (classic)**.
2.  Click **Generate new token** and select **Generate new token (classic)**.
3.  Configure the token settings:
    *   **Note:** Enter a descriptive name (e.g., `BreachRadar-Classic`).
    *   **Expiration:** Select an expiration period.
4.  **Select Scopes:**
    *   > [!IMPORTANT]
    *   > **For Public Search:** Do **NOT** select any checkboxes. Leave all scopes blank. This creates a secure read-only token for public data.
    *   **For Private Search:** Select the **`repo`** scope (or `public_repo` if you only want to access public repos you have write access to, though leaving all blank is preferred for public search).
5.  Click **Generate token**.
6.  Copy the token immediately.

---

### ⚙️ Configuration in BreachRadar
Once you have retrieved your token, add it to your project:

1.  Open your `.env` file in the project root.
2.  Locate or add the `GITHUB_TOKEN` variable and paste your token:
    ```env
    GITHUB_TOKEN=github_pat_xxxxxx
    ```
3.  Alternatively, you can configure it via the BreachRadar WebUI under **Settings** > **API Keys**.

***

## Version Française

Ce guide explique comment générer un jeton d'accès personnel GitHub (PAT) pour authentifier le moteur de recherche de BreachRadar.

L'utilisation d'un jeton augmente la limite de requêtes de l'API de recherche GitHub de **60 requêtes/heure** (non authentifié) à **5 000 requêtes/heure** (authentifié).

### 🛡️ Bonnes pratiques de sécurité (Moindre Privilège)
Pour protéger votre compte GitHub, n'attribuez toujours que les permissions minimales nécessaires :
*   **Pour les dépôts publics (Recommandé) :** Si vous surveillez uniquement les dépôts publics, générez un jeton avec **aucune permission/portée (scope) cochée**. Cela crée un jeton sécurisé en lecture seule.
*   **Pour les dépôts privés :** N'accordez des droits de lecture aux dépôts privés que si vous avez spécifiquement besoin de BreachRadar pour surveiller le code de vos dépôts privés ou d'organisation.
*   **Ne cochez jamais** de droits d'administration (`admin`), d'écriture (`write:*`) ou de suppression (`delete:*`).

---

### Méthode 1 : Jetons d'accès personnels de type "Fine-grained" (Recommandé)
Les jetons fins (fine-grained) représentent le standard de sécurité moderne de GitHub, offrant un contrôle plus précis.

1.  Connectez-vous à votre compte GitHub et allez sur [github.com](https://github.com).
2.  Dans le coin supérieur droit, cliquez sur votre photo de profil, puis sur **Settings** (Paramètres).
3.  Dans la colonne de gauche, faites défiler vers le bas et cliquez sur **Developer settings**.
4.  Dans la colonne de gauche, sous **Personal access tokens**, cliquez sur **Fine-grained tokens**.
5.  Cliquez sur **Generate new token**.
6.  Configurez les paramètres du jeton :
    *   **Token name :** Saisissez un nom descriptif (ex: `BreachRadar-Code-Search`).
    *   **Expiration :** Sélectionnez une période d'expiration (ex: 30, 60 ou 90 jours).
    *   **Description :** (Optionnel) Saisissez la finalité.
    *   **Resource owner :** Sélectionnez votre compte (ou organisation).
7.  Sous **Repository access** :
    *   Sélectionnez **Public repositories (read-only)** si vous surveillez uniquement le code public.
    *   Sélectionnez **All repositories** ou **Only select repositories** si vous devez surveiller des dépôts privés.
8.  Sous **Permissions** -> **Repository permissions** :
    *   **Metadata :** Assurez-vous que l'accès est défini sur **Read-only** (requis et activé par défaut).
    *   **Contents :** Définissez sur **Read-only** (requis uniquement si vous devez scanner des dépôts privés).
    *   Laissez toutes les autres permissions sur **No access**.
9.  Cliquez sur **Generate token**.
10. Copiez immédiatement le jeton généré. **Il ne sera plus affiché par la suite.**

---

### Méthode 2 : Jetons d'accès personnels de type "Classic" (Alternative)
Les jetons classiques sont l'ancien format, utile si les jetons fins rencontrent des problèmes de compatibilité.

1.  Allez dans **Settings** > **Developer settings** > **Personal access tokens** > **Tokens (classic)**.
2.  Cliquez sur **Generate new token** et sélectionnez **Generate new token (classic)**.
3.  Configurez les paramètres du jeton :
    *   **Note :** Saisissez un nom descriptif (ex: `BreachRadar-Classic`).
    *   **Expiration :** Sélectionnez une période d'expiration.
4.  **Sélection des Scopes (Portées) :**
    *   > [!IMPORTANT]
    *   > **Pour la recherche publique :** Ne cochez **AUCUNE** case. Laissez toutes les portées vides. Cela crée un jeton sécurisé en lecture seule pour les données publiques.
    *   **Pour la recherche privée :** Cochez la case **`repo`**.
5.  Cliquez sur **Generate token**.
6.  Copiez immédiatement le jeton généré.

---

### ⚙️ Configuration dans BreachRadar
Une fois votre jeton récupéré, ajoutez-le à votre projet :

1.  Ouvrez votre fichier `.env` à la racine du projet.
2.  Trouvez ou ajoutez la variable `GITHUB_TOKEN` et collez votre jeton :
    ```env
    GITHUB_TOKEN=github_pat_xxxxxx
    ```
3.  Alternativement, vous pouvez le configurer via l'interface Web de BreachRadar dans **Settings** > **API Keys**.
