PYTHON := python
MANAGE := $(PYTHON) manage.py

.PHONY: help install install-dev check migrate migrations makemigrations test test-users test-organizations test-education test-course test-assignments test-feedback test-journal lint format format-check precommit precommit-install coverage clean clean-pyc clean-cache clean-logs clean-media superuser shell runserver celery-worker celery-beat

help:
	@echo "Available commands:"
	@echo "  make install              Install base requirements"
	@echo "  make install-dev          Install dev requirements"
	@echo "  make check                Run Django system checks"
	@echo "  make migrate              Apply migrations"
	@echo "  make migrations           Check that migrations are committed"
	@echo "  make makemigrations       Create migrations"
	@echo "  make test                 Run all tests"
	@echo "  make lint                 Run Ruff linter"
	@echo "  make format               Format code with Ruff"
	@echo "  make format-check         Check formatting without changes"
	@echo "  make precommit-install    Install pre-commit hooks"
	@echo "  make precommit            Run pre-commit for all files"
	@echo "  make coverage             Run tests with coverage"
	@echo "  make clean                Remove local generated files"

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements/base.txt

install-dev:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements/dev.txt

check:
	$(MANAGE) check

migrate:
	$(MANAGE) migrate

migrations:
	$(MANAGE) makemigrations --check --dry-run

makemigrations:
	$(MANAGE) makemigrations

test:
	$(MANAGE) test

test-users:
	$(MANAGE) test apps.users

test-organizations:
	$(MANAGE) test apps.organizations

test-education:
	$(MANAGE) test apps.education

test-course:
	$(MANAGE) test apps.course

test-assignments:
	$(MANAGE) test apps.assignments

test-feedback:
	$(MANAGE) test apps.feedback

test-journal:
	$(MANAGE) test apps.journal

lint:
	ruff check .

format:
	ruff format .
	ruff check . --fix

format-check:
	ruff format . --check
	ruff check .

precommit-install:
	pre-commit install

precommit:
	pre-commit run --all-files

coverage:
	coverage run manage.py test
	coverage report -m

shell:
	$(MANAGE) shell

runserver:
	$(MANAGE) runserver

superuser:
	$(MANAGE) createsuperuser

celery-worker:
	celery -A config worker -l info

celery-beat:
	celery -A config beat -l info

clean: clean-pyc clean-cache clean-logs

clean-pyc:
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "__pycache__" -type d -prune -exec rm -rf {} +

clean-cache:
	rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov .coverage coverage.xml

clean-logs:
	rm -f logs/*.log

clean-media:
	rm -rf media/*
