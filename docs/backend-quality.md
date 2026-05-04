# Backend quality, CI and security checks

Этот документ фиксирует текущий backend quality pipeline проекта EDU-Pifagor.

## Основная команда

```bash
cd backend
make ci
```

`make ci` должен проходить перед push / pull request и перед началом крупной новой разработки.

## Проверки

Pipeline включает:

- `ruff check .` — lint;
- `ruff format . --check` — проверка форматирования;
- `makemigrations --check --dry-run` — проверка отсутствия незакоммиченных миграций;
- `manage.py check --settings=config.settings.testing` — Django system check;
- `make check-prod` — production deploy check;
- `make coverage` — тесты с coverage threshold.

Дополнительные security-команды:

```bash
make audit-deps
make audit-code
make audit
```

## Production deploy check

`make check-prod` запускает:

```bash
python manage.py check --deploy --settings=config.settings.prod
```

Для локальной и CI-проверки используются безопасные placeholder-значения окружения. Реальные production-секреты не должны храниться в репозитории.

## Coverage

Coverage запускается через:

```bash
make coverage
```

Threshold задается переменной `COVERAGE_FAIL_UNDER` в `Makefile` или при запуске:

```bash
make coverage COVERAGE_FAIL_UNDER=70
```

## Dependency audit

Проверка зависимостей:

```bash
make audit-deps
```

Используется `pip-audit` и файл `requirements/dev.txt`, который включает base-зависимости.

## Static security audit

Проверка Python-кода:

```bash
make audit-code
```

Используется `bandit`. Обычно из проверки исключаются тесты и миграции.

## Рекомендации

- Не смешивать feature-разработку и крупный OpenAPI cleanup в одном коммите.
- После изменения моделей всегда запускать `make migrations-check`.
- После изменения security/settings/CI всегда запускать `make ci`.
- Если `pip-audit` нашел CVE, сначала проверить доступность безопасной версии пакета, затем обновить зависимость отдельным коммитом.
