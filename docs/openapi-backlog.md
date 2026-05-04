# OpenAPI cleanup backlog

Проект использует `drf-spectacular` для генерации OpenAPI-схемы.

## Текущий статус

Базовая генерация схемы подключена. При production/system checks могут оставаться предупреждения `drf-spectacular.W001` и `drf-spectacular.W002`.

Эти предупреждения не означают, что backend endpoints не работают. Они показывают, что OpenAPI-схема недостаточно точно описывает часть API.

## Основные категории предупреждений

### SerializerMethodField type hints

Пример:

```text
unable to resolve type hint for function get_profile
```

Решение:

- добавить return type hints;
- или использовать `@extend_schema_field`.

### APIView without serializer_class

Пример:

```text
unable to guess serializer
```

Решение:

- добавить `serializer_class`;
- перейти на `GenericAPIView`, если это уместно;
- добавить `@extend_schema(request=..., responses=...)`.

### operationId collisions

Пример:

```text
operationId ... has collisions
```

Решение:

- добавить явный `operation_id` через `@extend_schema`;
- проверить пересекающиеся пути list/detail/action endpoints.

### enum naming collisions

Пример:

```text
enum naming encountered collision for fields named status
```

Решение:

- добавить `ENUM_NAME_OVERRIDES` в `SPECTACULAR_SETTINGS`;
- или переименовать поля/serializers так, чтобы схема получала уникальные имена enum.

## Приоритет cleanup

1. `users` auth/profile endpoints.
2. `organizations` service/action endpoints.
3. `course` list/detail/action endpoints.
4. `assignments` analytics/actions/review endpoints.
5. `feedback` public/admin endpoints.
6. `journal` action endpoints.

## Рекомендуемый подход

- Закрывать OpenAPI warnings по одному приложению за раз.
- Не смешивать OpenAPI cleanup с бизнес-логикой.
- После каждого этапа запускать:

```bash
cd backend
make check-prod
make ci
```
