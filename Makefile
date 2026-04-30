# Makefile — LeakMonitor
# Commandes standardisées pour développement, tests et déploiement
# Usage : make <target>

.PHONY: install test test-ransomlook test-integration lint type-check \
        scan scan-ransom report clean sources-status \
        ransomlook-up ransomlook-down ransomlook-check ransomlook-update ransomlook-logs \
        docker-build docker-run help

# ─── Variables ───────────────────────────────────────────────────────────────
TARGET_DOMAIN ?= $(shell grep TARGET_DOMAIN .env 2>/dev/null | cut -d= -f2)
PYTHON = uv run python
PYTEST = uv run pytest

# ─── Installation ────────────────────────────────────────────────────────────
install:
	uv sync

install-dev:
	uv sync --extra dev

# ─── Tests ───────────────────────────────────────────────────────────────────
test:
	$(PYTEST) tests/unit/ -v --cov=leakmonitor --cov-report=html --cov-report=term-missing

test-ransomlook:
	$(PYTEST) tests/test_clients/test_ransomlook.py tests/test_ransom_tracker.py -v

test-security:
	$(PYTEST) tests/test_security.py -v

test-integration:
	$(PYTEST) tests/integration/ --api-keys-required -v

# ─── Qualité de code ─────────────────────────────────────────────────────────
lint:
	uv run ruff check leakmonitor/ tests/
	uv run ruff format --check leakmonitor/ tests/

lint-fix:
	uv run ruff check --fix leakmonitor/ tests/
	uv run ruff format leakmonitor/ tests/

type-check:
	uv run mypy leakmonitor/

# ─── Scans ───────────────────────────────────────────────────────────────────
scan:
	$(PYTHON) -m leakmonitor scan

scan-ransom:
	$(PYTHON) -m leakmonitor ransomlook --check

scan-email:
	@read -p "Email à vérifier : " email; \
	$(PYTHON) -m leakmonitor check --email $$email

# ─── Rapports ────────────────────────────────────────────────────────────────
report:
	$(PYTHON) -m leakmonitor scan --format markdown,json,html

sources-status:
	$(PYTHON) -m leakmonitor sources --status

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

ransomlook-logs:
	docker compose logs -f ransomlook-app

ransomlook-groups:
	@echo "─── Groupes ransomware suivis ─────────────────────"
	@curl -s http://localhost:8888/api/v1/groups | python3 -c \
		"import sys, json; g=json.load(sys.stdin); print(f'{len(g)} groupes actifs')"

ransomlook-backup:
	@echo "─── Sauvegarde Redis RansomLook ───────────────────"
	docker compose exec ransomlook-redis redis-cli BGSAVE
	@echo "✅ Sauvegarde déclenchée"

# ─── Docker — LeakMonitor ────────────────────────────────────────────────────
docker-build:
	docker build -t leakmonitor:latest .

docker-run:
	docker compose up --build

docker-down:
	docker compose down

# ─── Aide ────────────────────────────────────────────────────────────────────
help:
	@echo "LeakMonitor — Commandes disponibles"
	@echo ""
	@echo "  Installation :"
	@echo "    install           Installer les dépendances"
	@echo "    install-dev       Installer les dépendances + outils de dev"
	@echo ""
	@echo "  Tests :"
	@echo "    test              Tests unitaires (avec couverture)"
	@echo "    test-ransomlook   Tests spécifiques RansomLook"
	@echo "    test-security     Tests de non-régression sécurité"
	@echo "    test-integration  Tests d'intégration (nécessite clés API)"
	@echo ""
	@echo "  Qualité :"
	@echo "    lint              Vérification ruff"
	@echo "    lint-fix          Correction automatique ruff"
	@echo "    type-check        Vérification mypy"
	@echo ""
	@echo "  Scans :"
	@echo "    scan              Scan complet"
	@echo "    scan-ransom       Scan RansomLook uniquement (urgence)"
	@echo "    report            Rapport complet (JSON + MD + HTML)"
	@echo ""
	@echo "  RansomLook :"
	@echo "    ransomlook-up     Démarrer Docker RansomLook"
	@echo "    ransomlook-down   Arrêter Docker RansomLook"
	@echo "    ransomlook-check  Vérifier état + rechercher le domaine"
	@echo "    ransomlook-update Mettre à jour l'image"
	@echo "    ransomlook-logs   Afficher les logs en temps réel"
	@echo ""
	@echo "  Docker :"
	@echo "    docker-build      Builder l'image LeakMonitor"
	@echo "    docker-run        Démarrer la stack complète"
	@echo "    clean             Nettoyer caches et rapports"
