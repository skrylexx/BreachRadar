# Makefile — BreachRadar WebUI
# Commandes standardisées pour développement, tests et déploiement
# Usage : make <target>

.PHONY: install install-backend install-frontend test test-security lint type-check \
        clean ransomlook-up ransomlook-down ransomlook-check ransomlook-update \
        docker-build docker-run docker-down help

# ─── Variables ───────────────────────────────────────────────────────────────
TARGET_DOMAIN ?= $(shell grep TARGET_DOMAIN .env 2>/dev/null | cut -d= -f2)

# ─── Installation ────────────────────────────────────────────────────────────
install: install-backend install-frontend

install-backend:
	cd backend && uv sync --extra dev

install-frontend:
	cd frontend && npm install

# ─── Tests (Backend) ─────────────────────────────────────────────────────────
test:
	cd backend && uv run pytest tests/ -v

test-security:
	cd backend && uv run pytest tests/test_security.py -v

# ─── Qualité de code (Backend) ───────────────────────────────────────────────
lint:
	cd backend && uv run ruff check app/ tests/
	cd backend && uv run ruff format --check app/ tests/

lint-fix:
	cd backend && uv run ruff check --fix app/ tests/
	cd backend && uv run ruff format app/ tests/

type-check:
	cd backend && uv run mypy app/

# ─── Nettoyage ───────────────────────────────────────────────────────────────
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null; true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null; true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null; true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null; true
	rm -f reports/*.json reports/*.md reports/*.html reports/*.pdf .coverage

# ─── RansomLook — Commandes Docker ───────────────────────────────────────────
ransomlook-up:
	docker compose up ransomlook-redis ransomlook-tor ransomlook-app -d
	@echo "⏳ Démarrage RansomLook en cours..."
	@echo "   Premier scraping : 10-30 minutes selon disponibilité Tor"
	@sleep 5
	@docker compose logs --tail=20 ransomlook-app

ransomlook-down:
	docker compose stop ransomlook-redis ransomlook-tor ransomlook-app

ransomlook-check:
	@echo "─── Statistiques RansomLook ───────────────────────"
	@curl -s http://localhost:8888/api/v1/stats | python3 -m json.tool
	@echo ""
	@echo "─── Recherche du domaine cible : $(TARGET_DOMAIN) ──"
	@curl -s "http://localhost:8888/api/v1/victim?name=$(TARGET_DOMAIN)" | python3 -m json.tool

ransomlook-update:
	docker compose pull ransomlook-app
	docker compose up -d ransomlook-app
	@echo "✅ Image RansomLook mise à jour"

# ─── Docker — BreachRadar WebUI ──────────────────────────────────────────────
docker-build:
	docker compose build

docker-run:
	docker compose up -d

docker-down:
	docker compose down

# ─── Aide ────────────────────────────────────────────────────────────────────
help:
	@echo "BreachRadar WebUI — Commandes disponibles"
	@echo ""
	@echo "  Installation :"
	@echo "    install           Installer backend (uv) et frontend (npm)"
	@echo ""
	@echo "  Tests & Qualité :"
	@echo "    test              Tests backend unitaires & intégration"
	@echo "    lint              Vérification ruff"
	@echo "    type-check        Vérification mypy"
	@echo ""
	@echo "  Docker :"
	@echo "    docker-build      Builder les images WebUI"
	@echo "    docker-run        Démarrer la stack complète"
	@echo "    docker-down       Arrêter la stack complète"
	@echo "    clean             Nettoyer caches"
