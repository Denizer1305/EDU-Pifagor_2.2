from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.response import Response

from apps.assignments.selectors import (
    get_submission_answers_queryset,
    get_submission_by_id,
    get_submission_review_by_id,
)


def validation_error_response(exc: DjangoValidationError | ValueError) -> Response:
    """Преобразует доменную ошибку в DRF Response."""

    if hasattr(exc, "message_dict"):
        payload = exc.message_dict
    elif hasattr(exc, "messages"):
        payload = {"detail": exc.messages}
    else:
        payload = {"detail": [str(exc)]}

    return Response(payload, status=status.HTTP_400_BAD_REQUEST)


def can_manage_submission_review(user, review) -> bool:
    """Проверяет, может ли пользователь управлять проверкой сдачи."""

    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return review.submission.assignment.author_id == user.id


def can_manage_submission(user, submission) -> bool:
    """Проверяет, может ли пользователь управлять сдачей."""

    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return submission.assignment.author_id == user.id


def get_submission_or_none(submission_id: int):
    """Возвращает сдачу по id или None."""

    return get_submission_by_id(submission_id=submission_id)


def get_review_or_none(review_id: int | None):
    """Возвращает проверку сдачи по id или None."""

    if not review_id:
        return None

    return get_submission_review_by_id(review_id=review_id)


def get_submission_answer_or_none(answer_id: int | None):
    """Возвращает ответ студента по id или None."""

    if not answer_id:
        return None

    return get_submission_answers_queryset().filter(id=answer_id).first()


def get_review_id_from_request(request, review_id: int | None = None) -> int | None:
    """
    Возвращает review_id из URL или тела запроса.

    Нужно для совместимости с двумя маршрутами:
    - reviews/<int:review_id>/comments/
    - reviews/comments/
    """

    if review_id is not None:
        return review_id

    raw_review_id = request.data.get("review_id")
    if raw_review_id in (None, ""):
        return None

    try:
        return int(raw_review_id)
    except (TypeError, ValueError):
        return None
