from __future__ import annotations


def _has_model_field(model, field_name: str) -> bool:
    """Проверяет, есть ли поле в модели.

    Используется для безопасной фильтрации по полям, которые могли быть
    удалены или ещё не добавлены в текущей версии модели.
    """

    return field_name in {field.name for field in model._meta.get_fields()}


def _filter_exact_if_field_exists(queryset, model, field_name: str, value):
    """Применяет exact-фильтр, если поле существует в модели."""

    if value in (None, ""):
        return queryset

    if not _has_model_field(model, field_name):
        return queryset

    return queryset.filter(**{field_name: value})


def _filter_gte_if_field_exists(queryset, model, field_name: str, value):
    """Применяет gte-фильтр, если поле существует в модели."""

    if value in (None, ""):
        return queryset

    if not _has_model_field(model, field_name):
        return queryset

    return queryset.filter(**{f"{field_name}__gte": value})


def _filter_lte_if_field_exists(queryset, model, field_name: str, value):
    """Применяет lte-фильтр, если поле существует в модели."""

    if value in (None, ""):
        return queryset

    if not _has_model_field(model, field_name):
        return queryset

    return queryset.filter(**{f"{field_name}__lte": value})
