# Backend tests

Папка `tests/` содержит верхнеуровневую инфраструктуру тестирования backend-проекта.

## Что здесь хранится
- общие фикстуры;
- базовые тестовые настройки;
- вспомогательные фабрики;
- API helper-функции;
- reusable assertions;
- smoke/integration/regression tests верхнего уровня.

## Что НЕ хранить
- предметные тесты конкретных приложений (`users`, `courses`, `assignments` и т.д.);
- бизнес-логику;
- factories, которые относятся только к одному app.

Такие тесты должны жить внутри:
- `apps/users/tests/`
- `apps/courses/tests/`
- `apps/assignments/tests/`
и т.д.
