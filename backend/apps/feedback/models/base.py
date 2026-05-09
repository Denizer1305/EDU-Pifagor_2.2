from __future__ import annotations

from django.db import models


def normalize_text(value: str | None) -> str:
    if value is None:
        return ""
    return value.strip()


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Создано",
        db_index=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Обновлено",
    )

    class Meta:
        abstract = True
