# Makefile for Prayer Wall project

RUN := uv run
PY := $(RUN) python
MANAGE := $(PY) manage.py

.DEFAULT_GOAL := help

.PHONY: help venv install deps migrate makemigrations runserver run test lint format collectstatic createsuperuser clean prod-gunicorn shell

help: ## Show this help message
	@echo "Prayer Wall Makefile - available targets:"
	@awk 'BEGIN {FS=":.*?## "} /^[a-zA-Z0-9_-]+:.*?##/ {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

venv: ## Create a virtualenv in $(VENV)
	@if [ -d "$(VENV)" ]; then echo "Virtualenv $(VENV) already exists"; exit 0; fi
	uv venv

install: venv ## Install project dependencies into the virtualenv
	uv sync

deps: install ## Alias for install

migrate: ## Run Django migrations
	$(MANAGE) migrate

makemigrations: ## Create new Django migrations for changes
	$(MANAGE) makemigrations

runserver: ## Run Django development server (defaults to config.settings.development)
	$(MANAGE) runserver

run: runserver ## Alias for runserver

test: ## Run Django tests using test settings (config.settings.test)
	$(MANAGE) test --settings=config.settings.test

createsuperuser: ## Create a Django superuser (interactive)
	$(MANAGE) createsuperuser

collectstatic: ## Collect static files
	$(MANAGE) collectstatic --noinput

shell: ## Open Django shell
	$(MANAGE) shell

check: ## check Django project for issues (migrations, staticfiles, etc.)
	$(MANAGE) check

lint: ## Run ruff linter (if available)
	$(RUN) ruff check . --fix
format: ## Run ruff format (if available)
	$(RUN) ruff format .

prod-gunicorn: ## Run a production Gunicorn server (expects env vars set)
	$(RUN) gunicorn config.wsgi:application --workers 4 --bind 0.0.0.0:8000

clean: ## Remove Python artifacts, caches, and local sqlite db
	@echo "Cleaning project..."
	rm -rf .pytest_cache/ .mypy_cache/ __pycache__ */__pycache__ .venv/ build/ dist/ *.egg-info
	rm -f *.pyc
	rm -f db.sqlite3
	@echo "Clean complete"
