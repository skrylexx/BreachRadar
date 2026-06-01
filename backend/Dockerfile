# ─── Backend FastAPI — Dockerfile ───────────────────────────────────────────
# Image slim, non-root, avec uv pour la gestion des paquets
FROM python:3.12-slim@sha256:452a468a4bf985040037cb6d5392410206e47db9bf5b7278d281f94d1c2d0931 AS base

# Métadonnées
LABEL maintainer="BreachRadar Team"
LABEL description="BreachRadar WebUI — FastAPI Backend"

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_SYSTEM_PYTHON=1

# Installer les dépendances système minimales
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpango-1.0-0 \
    libharfbuzz0b \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

# Installer uv via l'image officielle (plus sécurisé que curl | sh)
COPY --from=ghcr.io/astral-sh/uv@sha256:34f919409ae82303e722cc625cfaa52bef090fb73dcd1ca5e6d999b2fe8337e5 /uv /uvx /bin/

WORKDIR /app

# Copier et installer les dépendances Python
COPY pyproject.toml ./
COPY README.md ./
RUN uv pip install --system ".[pdf]"

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
