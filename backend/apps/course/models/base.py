from __future__ import annotations

from uuid import uuid4

from django.db import models
from django.utils.text import slugify


def normalize_text(value: str | None) -> str:
    return (value or "").strip()


def generate_code(prefix: str = "CRS") -> str:
    return f"{prefix}-{uuid4().hex[:10].upper()}"


def build_unique_slug(
    model_class, value: str, instance=None, slug_field: str = "slug"
) -> str:
    base_slug = slugify(value) or uuid4().hex[:8]
    slug = base_slug
    counter = 2

    queryset = model_class.objects.all()
    if instance and instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    while queryset.filter(**{slug_field: slug}).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Создано",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Обновлено",
    )

    class Meta:
        abstract = True


class OrderedModel(models.Model):
    order = models.PositiveIntegerField(
        default=1,
        verbose_name="Порядок",
    )

    class Meta:
        abstract = True
        ordering = ("order", "id")
