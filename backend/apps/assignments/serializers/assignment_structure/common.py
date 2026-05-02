from __future__ import annotations

from rest_framework import serializers


def build_file_url(file_value, context: dict) -> str:
    """Возвращает абсолютный URL файла, если в context передан request."""

    if not file_value:
        return ""

    try:
        url = file_value.url
    except Exception:
        return ""

    request = context.get("request")
    return request.build_absolute_uri(url) if request else url


def validate_variant_belongs_to_assignment(
    *,
    assignment,
    variant,
    field_name: str = "variant_id",
) -> None:
    """Проверяет, что вариант принадлежит выбранной работе."""

    if (
        assignment is not None
        and variant is not None
        and variant.assignment_id != assignment.id
    ):
        raise serializers.ValidationError(
            {field_name: "Вариант должен принадлежать выбранной работе."}
        )


def validate_section_belongs_to_assignment(
    *,
    assignment,
    section,
    field_name: str = "section_id",
) -> None:
    """Проверяет, что секция принадлежит выбранной работе."""

    if (
        assignment is not None
        and section is not None
        and section.assignment_id != assignment.id
    ):
        raise serializers.ValidationError(
            {field_name: "Секция должна принадлежать выбранной работе."}
        )


def validate_section_belongs_to_variant(*, section, variant) -> None:
    """Проверяет, что секция относится к выбранному варианту."""

    if (
        variant is not None
        and section is not None
        and section.variant_id
        and section.variant_id != variant.id
    ):
        raise serializers.ValidationError(
            {"section_id": "Секция должна относиться к выбранному варианту."}
        )
