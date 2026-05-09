from __future__ import annotations


def build_absolute_media_url(request, file_field) -> str:
    """Возвращает абсолютный URL медиа-файла."""

    if not file_field:
        return ""

    try:
        url = file_field.url
    except Exception:
        return ""

    if request is not None:
        return request.build_absolute_uri(url)

    return url
