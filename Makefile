.PHONY: help dev dev-reset run test lint fmt clean docker-up docker-down docker-build \
       install db-reset db-migrate seed check

PYTHON   ?= python3
PORT     ?= 8000
HOST     ?= 127.0.0.1
DB_PATH  ?= prompts.db

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'

# ──────────────────────────── Development ────────────────────────────

install: ## Install Python dependencies
	$(PYTHON) -m pip install -r requirements.txt

dev: ## Start dev server with auto-reload
	uvicorn backend.main:app --host $(HOST) --port $(PORT) --reload

dev-reset: seed db-reset dev ## Rebuild index + reset DB + start dev server

run: ## Start production server
	uvicorn backend.main:app --host 0.0.0.0 --port $(PORT)

# ──────────────────────────── Testing ────────────────────────────────

test: ## Run all tests
	$(PYTHON) -m pytest backend/tests/ -v

test-cov: ## Run tests with coverage
	$(PYTHON) -m pytest backend/tests/ -v --cov=backend --cov-report=term-missing

lint: ## Run linter (ruff)
	$(PYTHON) -m ruff check backend/ scripts/

fmt: ## Auto-format code (ruff)
	$(PYTHON) -m ruff format backend/ scripts/
	$(PYTHON) -m ruff check --fix backend/ scripts/

check: lint test ## Lint + test

# ──────────────────────────── Database ───────────────────────────────

db-migrate: ## Run DB migration from .md files
	$(PYTHON) -c "import asyncio; from backend.migrate import migrate_all; asyncio.run(migrate_all())"

db-reset: ## Delete DB and re-migrate
	rm -f $(DB_PATH)
	$(MAKE) db-migrate

seed: ## Rebuild search index from .md files
	$(PYTHON) scripts/rebuild-index.py

# ──────────────────────────── Docker ─────────────────────────────────

docker-build: ## Build Docker image
	docker compose build

docker-up: ## Start with Docker Compose (detached)
	docker compose up -d

docker-down: ## Stop Docker Compose
	docker compose down

docker-logs: ## Tail Docker logs
	docker compose logs -f

# ──────────────────────────── Utilities ──────────────────────────────

clean: ## Remove caches and temp files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true

open: ## Open app in browser
	open http://$(HOST):$(PORT)

dev-open: dev-bg open ## Start dev server and open browser
dev-bg:
	@echo "Starting dev server in background..."
	@uvicorn backend.main:app --host $(HOST) --port $(PORT) --reload &
	@sleep 1
