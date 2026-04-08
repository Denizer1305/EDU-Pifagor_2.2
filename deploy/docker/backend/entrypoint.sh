#!/bin/sh
set -e

echo "Waiting for PostgreSQL at ${DB_HOST}:${DB_PORT}..."

while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 1
done

echo "PostgreSQL is up."

python manage.py migrate

python manage.py collectstatic --noinput || true

python manage.py runserver 0.0.0.0:8000
