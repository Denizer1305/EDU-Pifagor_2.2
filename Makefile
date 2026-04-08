.PHONY: help up down build restart logs bash-backend bash-frontend migrate makemigrations collectstatic test lint

help:
	@echo "Команды проекта:"
	@echo "  make up               - запуск dev окружения"
	@echo "  make down             - остановка контейнеров"
	@echo "  make build            - пересборка контейнеров"
	@echo "  make restart          - перезапуск dev окружения"
	@echo "  make logs             - просмотр логов"
	@echo "  make bash-backend     - shell в backend контейнере"
	@echo "  make bash-frontend    - shell во frontend контейнере"
	@echo "  make migrate          - применить миграции"
	@echo "  make makemigrations   - создать миграции"
	@echo "  make collectstatic    - собрать статику"
	@echo "  make test             - запуск backend тестов"

up:
	docker compose -f docker-compose.dev.yml up --build

down:
	docker compose -f docker-compose.dev.yml down

build:
	docker compose -f docker-compose.dev.yml build

restart: down up

logs:
	docker compose -f docker-compose.dev.yml logs -f

bash-backend:
	docker compose -f docker-compose.dev.yml exec backend sh

bash-frontend:
	docker compose -f docker-compose.dev.yml exec frontend sh

migrate:
	docker compose -f docker-compose.dev.yml exec backend python backend/manage.py migrate

makemigrations:
	docker compose -f docker-compose.dev.yml exec backend python backend/manage.py makemigrations

collectstatic:
	docker compose -f docker-compose.dev.yml exec backend python backend/manage.py collectstatic --noinput

test:
	docker compose -f docker-compose.dev.yml exec backend python backend/manage.py test
