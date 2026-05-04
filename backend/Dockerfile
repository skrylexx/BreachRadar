# ─── Backend FastAPI — Dockerfile ───────────────────────────────────────────
# Image slim, non-root, avec uv pour la gestion des paquets
FROM python:3.12-slim AS base

# Métadonnées
LABEL maintainer="BreachRadar Team"
LABEL description="BreachRadar WebUI — FastAPI Backend"

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1

# Installer uv + dépendances système minimales
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

WORKDIR /app

# Copier et installer les dépendances Python
COPY pyproject.toml ./
RUN uv pip install --system .

# Copier le code source
COPY app/ ./app/

# Utilisateur non-root
RUN groupadd -r brapi && useradd -r -g brapi brapi
RUN chown -R brapi:brapi /app
USER brapi

# Port exposé
EXPOSE 8000

# Point d'entrée — Uvicorn avec rechargement automatique désactivé en prod
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
