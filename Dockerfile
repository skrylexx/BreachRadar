# Dockerfile — BreachRadar
# Base : Python 3.12 slim pour minimiser la surface d'attaque
# Utilisateur non-root pour la sécurité en production

FROM python:3.12-slim AS base

# Métadonnées
LABEL maintainer="BreachRadar Team"
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
RUN uv sync --all-extras --no-install-project --no-dev

# Copier le code source
COPY breachradar/ ./breachradar/
COPY README.md ./
COPY LICENSE ./

# Installer le projet lui-même avec les extras
RUN uv sync --all-extras --no-dev

# ─── Stage de production ─────────────────────────────────────────────────────
FROM base AS production

WORKDIR /app

# Créer un utilisateur non-root pour la sécurité
RUN groupadd --gid 1000 breachradar && \
    useradd --uid 1000 --gid breachradar --shell /bin/bash --create-home breachradar

# Copier le venv et le code depuis le builder
COPY --from=builder --chown=breachradar:breachradar /app/.venv /app/.venv
COPY --from=builder --chown=breachradar:breachradar /app/breachradar /app/breachradar

# Créer le répertoire de rapports avec les bonnes permissions
RUN mkdir -p /app/reports && chown breachradar:breachradar /app/reports

# Passer à l'utilisateur non-root
USER breachradar

# Ajouter le venv au PATH
ENV PATH="/app/.venv/bin:$PATH"

# Volume pour les rapports générés
VOLUME ["/app/reports"]

# Point d'entrée : scheduler en arrière-plan par défaut
# Peut être overridé avec : docker run breachradar python -m breachradar scan
CMD ["python", "-m", "breachradar", "schedule", "--start"]
