.DEFAULT_GOAL := help

PYTHON ?= python3
MANAGE := $(PYTHON) manage.py

DJANGO_SETTINGS ?= config.settings.dev
TEST_SETTINGS ?= config.settings.testing

APP ?=

.PHONY: help \
	install install-dev precommit-install \
	run shell createsuperuser makemigrations migrations-check migrate showmigrations collectstatic \
	lint lint-fix format precommit check \
	test test-keepdb test-app test-users test-assignments test-course test-education \
	coverage coverage-html \
	clean clean-pyc clean-cache \
	ci

help: ## Show this help message
	@echo "Pifagor backend commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install              Install production dependencies"
	@echo "  make install-dev          Install development dependencies"
	@echo "  make precommit-install    Install pre-commit git hooks"
	@echo ""
	@echo "Django:"
	@echo "  make run                  Run development server"
	@echo "  make shell                Open Django shell"
	@echo "  make createsuperuser      Create Django superuser"
	@echo "  make makemigrations       Create migrations"
	@echo "  make migrations-check     Check that migrations are up to date"
	@echo "  make migrate              Apply migrations"
	@echo "  make showmigrations       Show migration status"
	@echo "  make collectstatic        Collect static files"
	@echo ""
	@echo "Quality:"
	@echo "  make lint                 Run Ruff lint"
	@echo "  make lint-fix             Run Ruff lint with fixes"
	@echo "  make format               Run Ruff formatter"
	@echo "  make precommit            Run all pre-commit hooks"
	@echo "  make check                Run Django system check"
	@echo ""
	@echo "Tests:"
	@echo "  make test                 Run all tests"
	@echo "  make test-keepdb          Run all tests with reused test DB"
	@echo "  make test-app APP=apps.users"
	@echo "  make test-users"
	@echo "  make test-assignments"
	@echo "  make test-course"
	@echo "  make test-education"
	@echo ""
	@echo "Coverage:"
	@echo "  make coverage             Run tests with coverage"
	@echo "  make coverage-html        Generate HTML coverage report"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean                Remove Python cache files and tool caches"
	@echo ""
	@echo "CI:"
	@echo "  make ci                   Run checks used in CI"

install: ## Install production dependencies
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements/base.txt

install-dev: ## Install development dependencies
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements/dev.txt

precommit-install: ## Install pre-commit git hooks
	$(PYTHON) -m pre_commit install

run: ## Run development server
	$(MANAGE) runserver --settings=$(DJANGO_SETTINGS)

shell: ## Open Django shell
	$(MANAGE) shell --settings=$(DJANGO_SETTINGS)

createsuperuser: ## Create Django superuser
	$(MANAGE) createsuperuser --settings=$(DJANGO_SETTINGS)

makemigrations: ## Create migrations
	$(MANAGE) makemigrations --settings=$(DJANGO_SETTINGS)

migrations-check: ## Check that migrations are up to date
	$(MANAGE) makemigrations --check --dry-run --settings=$(TEST_SETTINGS)

migrate: ## Apply migrations
	$(MANAGE) migrate --settings=$(DJANGO_SETTINGS)

showmigrations: ## Show migration status
	$(MANAGE) showmigrations --settings=$(DJANGO_SETTINGS)

collectstatic: ## Collect static files
	$(MANAGE) collectstatic --noinput --settings=$(DJANGO_SETTINGS)

lint: ## Run Ruff lint
	$(PYTHON) -m ruff check .

lint-fix: ## Run Ruff lint with fixes
	$(PYTHON) -m ruff check . --fix

format: ## Run Ruff formatter
	$(PYTHON) -m ruff format .

precommit: ## Run all pre-commit hooks
	$(PYTHON) -m pre_commit run --all-files

check: ## Run Django system check
	$(MANAGE) check --settings=$(TEST_SETTINGS)

test: ## Run all tests
	$(MANAGE) test --settings=$(TEST_SETTINGS)

test-keepdb: ## Run all tests with reused test DB
	$(MANAGE) test --keepdb --settings=$(TEST_SETTINGS)

test-app: ## Run tests for one app: make test-app APP=apps.users
ifndef APP
	$(error APP is not set. Example: make test-app APP=apps.users)
endif
	$(MANAGE) test $(APP) --settings=$(TEST_SETTINGS)

test-users: ## Run users tests
	$(MANAGE) test apps.users --settings=$(TEST_SETTINGS)

test-assignments: ## Run assignments tests
	$(MANAGE) test apps.assignments --settings=$(TEST_SETTINGS)

test-course: ## Run course tests
	$(MANAGE) test apps.course --settings=$(TEST_SETTINGS)

test-education: ## Run education tests
	$(MANAGE) test apps.education --settings=$(TEST_SETTINGS)

coverage: ## Run tests with coverage
	$(PYTHON) -m coverage run manage.py test --settings=$(TEST_SETTINGS)
	$(PYTHON) -m coverage report

coverage-html: ## Generate HTML coverage report
	$(PYTHON) -m coverage html

clean: clean-pyc clean-cache ## Remove Python cache files and tool caches

clean-pyc: ## Remove Python cache files
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

clean-cache: ## Remove tool caches
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf coverage.xml

ci: ## Run checks used in CI
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format . --check
	$(MANAGE) makemigrations --check --dry-run --settings=$(TEST_SETTINGS)
	$(MANAGE) check --settings=$(TEST_SETTINGS)
	$(MANAGE) test --settings=$(TEST_SETTINGS)
