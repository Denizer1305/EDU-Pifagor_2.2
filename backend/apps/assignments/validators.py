from __future__ import annotations

import os
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError

ASSIGNMENT_ALLOWED_FILE_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".zip",
    ".rar",
    ".7z",
    ".txt",
    ".csv",
}

ASSIGNMENT_MAX_FILE_SIZE = 25 * 1024 * 1024


def validate_non_negative_number(value, field_name: str = "value") -> None:
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValidationError({field_name: "Значение должно быть числом."}) from exc

    if number < 0:
        raise ValidationError({field_name: "Значение не может быть отрицательным."})


def validate_percentage(value, field_name: str = "value") -> None:
    try:
        number = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValidationError({field_name: "Значение должно быть числом."}) from exc

    if number < 0 or number > 100:
        raise ValidationError(
            {field_name: "Значение должно быть в диапазоне от 0 до 100."}
        )


def validate_positive_order(value, field_name: str = "order") -> None:
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise ValidationError(
            {field_name: "Порядок должен быть целым числом."}
        ) from exc

    if number <= 0:
        raise ValidationError({field_name: "Порядок должен быть больше 0."})


def validate_uploaded_file(
    uploaded_file,
    *,
    field_name: str = "file",
    allowed_extensions: set[str] | None = None,
    max_file_size: int = ASSIGNMENT_MAX_FILE_SIZE,
) -> None:
    if uploaded_file is None:
        raise ValidationError({field_name: "Файл обязателен."})

    allowed_extensions = allowed_extensions or ASSIGNMENT_ALLOWED_FILE_EXTENSIONS
    file_name = getattr(uploaded_file, "name", "") or ""
    file_size = getattr(uploaded_file, "size", 0) or 0

    ext = os.path.splitext(file_name)[1].lower()
    if ext and ext not in allowed_extensions:
        raise ValidationError(
            {
                field_name: (
                    "Недопустимый формат файла. "
                    "Разрешены: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, изображения, архивы, TXT, CSV."
                )
            }
        )

    if file_size > max_file_size:
        raise ValidationError(
            {
                field_name: f"Размер файла не должен превышать {max_file_size // (1024 * 1024)} МБ."
            }
        )
