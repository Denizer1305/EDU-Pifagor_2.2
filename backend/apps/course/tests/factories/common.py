from __future__ import annotations

from itertools import count

from django.core.files.uploadedfile import SimpleUploadedFile

course_counter = count(1)
module_counter = count(1)
lesson_counter = count(1)
material_counter = count(1)
assignment_counter = count(1)
enrollment_counter = count(1)


def _unwrap_factory_result(value):
    """Возвращает объект из фабрики, если фабрика вернула tuple."""

    if isinstance(value, tuple):
        return value[0]

    return value


def create_course_file(
    *,
    name: str | None = None,
    content: bytes | None = None,
    content_type: str = "application/pdf",
):
    """Создаёт тестовый файл для материалов курса."""

    index = next(material_counter)

    if name is None:
        name = f"course-file-{index}.pdf"

    if content is None:
        content = b"test file content"

    return SimpleUploadedFile(
        name=name,
        content=content,
        content_type=content_type,
    )
