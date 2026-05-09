from __future__ import annotations

import uuid

from django.core.files.uploadedfile import SimpleUploadedFile


def short_uuid() -> str:
    """Возвращает короткий uuid для уникальных тестовых значений."""

    return uuid.uuid4().hex[:8]


def unique_email(prefix: str) -> str:
    """Возвращает уникальный email для тестового пользователя."""

    return f"{prefix}_{short_uuid()}@example.com"


def extract_user(created):
    """Достаёт пользователя из результата фабрики, если она вернула tuple."""

    if isinstance(created, tuple):
        return created[0]

    return created


def create_test_pdf_file(
    *,
    name: str = "test.pdf",
    content: bytes = b"%PDF-1.4 test file",
) -> SimpleUploadedFile:
    """Создаёт простой PDF-файл для тестов загрузки."""

    return SimpleUploadedFile(
        name,
        content,
        content_type="application/pdf",
    )
