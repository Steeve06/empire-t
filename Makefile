SHELL := /bin/bash
COMPOSE := docker compose --env-file .env -f infra/docker-compose.yml
PROD := docker compose --env-file .env.production -f infra/docker-compose.prod.yml
API := $(COMPOSE) exec api
API_RUN := $(COMPOSE) run --rm --no-deps api

.DEFAULT_GOAL := help
.PHONY: help env dev up down logs build migrate makemigrations seed superuser bootstrap \
	test test-api test-web lint lint-api lint-web format typecheck schema api-client shell \
	install web-build prerender messages \
	prod-https prod-deploy prod-bootstrap prod-logs prod-refresh prod-backup prod-restore

help: ## List available commands
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[33m%-16s\033[0m %s\n", $$1, $$2}'

env: ## Create .env from .env.example if missing
	@test -f .env || (cp .env.example .env && echo "Created .env from .env.example")

dev: env ## Start the full stack (db, redis, api, web) with live reload: site on :5173, API/admin on :8000
	$(COMPOSE) up --build

up: env ## Start the stack in the background
	$(COMPOSE) up --build -d

down: ## Stop the stack
	$(COMPOSE) down

logs: ## Follow logs from all services
	$(COMPOSE) logs -f

build: env ## Build all images
	$(COMPOSE) build

migrate: ## Apply database migrations
	$(API) python manage.py migrate

makemigrations: ## Create new migrations after model changes
	$(API) python manage.py makemigrations

seed: ## Load services, prices, openings and site settings (idempotent)
	$(API) python manage.py seed

superuser: ## Create the admin account from DJANGO_SUPERUSER_* variables (idempotent)
	$(API) python manage.py ensure_superuser

bootstrap: migrate seed superuser ## migrate + seed + superuser in one go

messages: ## Compile apps/api/locale/en/LC_MESSAGES/django.po after editing English API messages
	$(API) python manage.py compilemessages --ignore=.venv

shell: ## Django shell inside the api container
	$(API) python manage.py shell

test: test-api test-web ## Run every test suite

test-api: ## Backend tests with coverage
	$(API_RUN) sh -c "pytest"

test-web: ## Frontend and API-client tests (needs `make install` once)
	pnpm -r test

install: ## Install frontend dependencies on the host (Node 22 + pnpm via corepack)
	corepack enable && pnpm install --frozen-lockfile

web-build: ## Production build of the site (client bundle + pre-renderer)
	pnpm --filter @empire-t/web build

prerender: web-build ## Build, then render every page from the running API into apps/web/dist
	pnpm --filter @empire-t/web prerender

lint: lint-api lint-web ## Run every linter and type checker

lint-api: ## Ruff, Black (check), mypy
	$(API_RUN) sh -c "ruff check . && black --check . && mypy ."

lint-web: ## ESLint, Prettier (check), tsc
	pnpm -r lint && pnpm -r typecheck

format: ## Auto-format backend and frontend
	$(API_RUN) sh -c "ruff check --fix . && black ."
	pnpm -r format

typecheck: ## Type checks only
	$(API_RUN) mypy .
	pnpm -r typecheck

schema: ## Export the OpenAPI schema to packages/api-client/openapi.yaml
	$(API_RUN) python manage.py spectacular --file /api-client/openapi.yaml --validate --fail-on-warn

api-client: schema ## Regenerate TypeScript types from the OpenAPI schema
	pnpm --filter @empire-t/api-client generate

# ---- Production (on the server, see docs/deployment.md) ---------------------
prod-https: ## First start with a Let's Encrypt certificate (once per server)
	infra/scripts/init-letsencrypt.sh

prod-deploy: ## Pull the latest code, rebuild and restart with zero manual steps
	git pull --ff-only
	$(PROD) up -d --build --remove-orphans
	$(PROD) ps

prod-bootstrap: ## Load the seed content and create the admin account (first deploy)
	$(PROD) exec api python manage.py seed
	$(PROD) exec api python manage.py ensure_superuser

prod-logs: ## Follow production logs
	$(PROD) logs -f --tail=100

prod-refresh: ## Re-render the static pages now (instead of waiting for the hourly run)
	$(PROD) restart prerender

prod-backup: ## Back up the database and uploaded files to backups/
	infra/scripts/backup.sh

prod-restore: ## Restore: make prod-restore DB=backups/db-....dump MEDIA=backups/media-....tar.gz
	infra/scripts/restore.sh $(DB) $(MEDIA)
