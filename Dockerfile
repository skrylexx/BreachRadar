# Dockerfile — LeakMonitor
# Base : Python 3.12 slim pour minimiser la surface d'attaque
# Utilisateur non-root pour la sécurité en production

FROM python:3.12-slim AS base

# Métadonnées
LABEL maintainer="LeakMonitor Team"
LABEL description="Outil de détection de fuites de données — OSINT défensif"

# Variables d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Installer uv (gestionnaire de paquets ultra-rapide)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# ─── Stage de build ──────────────────────────────────────────────────────────
FROM base AS builder

WORKDIR /app

# Copier les fichiers de définition des dépendances en premier (cache Docker)
COPY pyproject.toml ./
COPY uv.lock* ./

# Installer les dépendances dans un venv isolé
RUN uv sync --frozen --no-install-project --no-dev

# Copier le code source
COPY leakmonitor/ ./leakmonitor/

# Installer le projet lui-même
RUN uv sync --frozen --no-dev

# ─── Stage de production ─────────────────────────────────────────────────────
FROM base AS production

WORKDIR /app

# Créer un utilisateur non-root pour la sécurité
RUN groupadd --gid 1000 leakmonitor && \
    useradd --uid 1000 --gid leakmonitor --shell /bin/bash --create-home leakmonitor

# Copier le venv et le code depuis le builder
COPY --from=builder --chown=leakmonitor:leakmonitor /app/.venv /app/.venv
COPY --from=builder --chown=leakmonitor:leakmonitor /app/leakmonitor /app/leakmonitor

# Créer le répertoire de rapports avec les bonnes permissions
RUN mkdir -p /app/reports && chown leakmonitor:leakmonitor /app/reports

# Passer à l'utilisateur non-root
USER leakmonitor

# Ajouter le venv au PATH
ENV PATH="/app/.venv/bin:$PATH"

# Volume pour les rapports générés
VOLUME ["/app/reports"]

# Point d'entrée : scheduler en arrière-plan par défaut
# Peut être overridé avec : docker run leakmonitor python -m leakmonitor scan
CMD ["python", "-m", "leakmonitor", "schedule", "--start"]
