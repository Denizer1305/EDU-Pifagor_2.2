from __future__ import annotations


def ids(queryset):
    return set(queryset.values_list("id", flat=True))
