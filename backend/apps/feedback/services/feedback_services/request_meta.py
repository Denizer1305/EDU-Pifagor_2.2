from __future__ import annotations

from apps.feedback.models.base import normalize_text


def _extract_request_meta(request) -> dict[str, str | None]:
    """Достаёт IP, User-Agent и referrer из Django request."""

    if request is None:
        return {
            "ip_address": None,
            "user_agent": "",
            "referrer": "",
        }

    meta = getattr(request, "META", {}) or {}

    forwarded_for = meta.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded_for:
        ip_address = forwarded_for.split(",")[0].strip()
    else:
        ip_address = meta.get("REMOTE_ADDR")

    return {
        "ip_address": ip_address,
        "user_agent": normalize_text(meta.get("HTTP_USER_AGENT", "")),
        "referrer": normalize_text(meta.get("HTTP_REFERER", "")),
    }
