from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.response import Response

from apps.assignments.permissions import CanManageAssignmentObject
from apps.assignments.selectors import get_assignment_by_id


def validation_error_response(exc: DjangoValidationError | ValueError) -> Response:
    """Преобразует доменные ошибки Django/сервисов в DRF-ответ."""

    if hasattr(exc, "message_dict"):
        payload = exc.message_dict
    elif hasattr(exc, "messages"):
        payload = {"detail": exc.messages}
    else:
        payload = {"detail": [str(exc)]}

    return Response(payload, status=status.HTTP_400_BAD_REQUEST)


def get_assignment_or_404(view, request, assignment_id: int):
    """
    Возвращает работу по id или None.

    Если работа найдена, дополнительно проверяет object-level permissions.
    """

    assignment = get_assignment_by_id(assignment_id=assignment_id)
    if assignment is None:
        return None

    view.check_object_permissions(request, assignment)
    return assignment


def check_assignment_object_permission(view, request, obj) -> None:
    """Проверяет доступ к объекту, связанному с Assignment."""

    checker = CanManageAssignmentObject()
    if not checker.has_object_permission(request, view, obj):
        view.permission_denied(request, message=checker.message)
