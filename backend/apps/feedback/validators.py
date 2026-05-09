from __future__ import annotations

import os

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

MAX_ATTACHMENTS_COUNT = 5
MAX_ATTACHMENT_SIZE = 10 * 1024 * 1024
MAX_ERROR_DETAILS_LENGTH = 10000

ALLOWED_ATTACHMENT_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".pdf",
    ".doc",
    ".docx",
}


def validate_feedback_message(value: str) -> str:
    value = (value or "").strip()

    if not value:
        raise ValidationError(_("Сообщение не может быть пустым."))

    if len(value) < 5:
        raise ValidationError(_("Сообщение должно содержать не менее 5 символов."))

    return value


def validate_error_details(value: str) -> str:
    value = (value or "").strip()

    if len(value) > MAX_ERROR_DETAILS_LENGTH:
        raise ValidationError(
            _("Технические детали ошибки не должны превышать 10000 символов.")
        )

    return value


def validate_feedback_attachments_count(files) -> list:
    files = list(files or [])

    if len(files) > MAX_ATTACHMENTS_COUNT:
        raise ValidationError(_("Можно прикрепить не более 5 файлов."))

    return files


def validate_attachment_extension(filename: str) -> str:
    ext = os.path.splitext(filename or "")[1].lower()

    if ext not in ALLOWED_ATTACHMENT_EXTENSIONS:
        raise ValidationError(_("Поддерживаются только изображения, PDF, DOC и DOCX."))

    return ext


def validate_attachment_size(file_obj) -> int:
    file_size = getattr(file_obj, "size", 0) or 0

    if file_size > MAX_ATTACHMENT_SIZE:
        raise ValidationError(_("Размер файла не должен превышать 10 МБ."))

    return file_size
