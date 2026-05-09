from __future__ import annotations


def clean_search_value(value) -> str:
    """Очищает поисковый query-параметр."""

    return (value or "").strip()
