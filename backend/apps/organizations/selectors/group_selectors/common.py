from __future__ import annotations


def _clean_str(value: str | None) -> str:
    """Очищает строковый параметр фильтрации."""

    return (value or "").strip()
