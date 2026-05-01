from __future__ import annotations


def user_payload(user):
    """Возвращает короткое представление пользователя."""

    if not user:
        return None

    full_name = ""
    if hasattr(user, "get_full_name"):
        full_name = user.get_full_name() or ""

    return {
        "id": user.id,
        "email": getattr(user, "email", "") or "",
        "full_name": full_name or getattr(user, "email", "") or "",
    }


def assignment_payload(assignment):
    """Возвращает короткое представление работы."""

    if not assignment:
        return None

    return {
        "id": assignment.id,
        "title": getattr(assignment, "title", "") or "",
        "status": getattr(assignment, "status", "") or "",
        "assignment_kind": getattr(assignment, "assignment_kind", "") or "",
    }


def publication_payload(publication):
    """Возвращает короткое представление публикации работы."""

    if not publication:
        return None

    return {
        "id": publication.id,
        "title_override": getattr(publication, "title_override", "") or "",
        "status": getattr(publication, "status", "") or "",
        "starts_at": getattr(publication, "starts_at", None),
        "due_at": getattr(publication, "due_at", None),
        "available_until": getattr(publication, "available_until", None),
    }


def build_file_url(file_value, context: dict) -> str:
    """Возвращает абсолютный URL файла, если доступен request."""

    if not file_value:
        return ""

    try:
        url = file_value.url
    except Exception:
        return ""

    request = context.get("request")
    return request.build_absolute_uri(url) if request else url
