from __future__ import annotations

from decimal import Decimal

from django.db.models import QuerySet, Sum


def sum_decimal(queryset: QuerySet, field_name: str) -> Decimal:
    """Суммирует Decimal-поле queryset и возвращает Decimal('0') вместо None."""

    value = queryset.aggregate(total=Sum(field_name)).get("total")
    return value or Decimal("0")
