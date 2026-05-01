from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assignments.permissions import IsTeacherOrAdmin
from apps.assignments.serializers import (
    AssignmentDetailSerializer,
    AssignmentDuplicateSerializer,
)
from apps.assignments.services import (
    archive_assignment,
    duplicate_assignment,
    publish_assignment,
)
from apps.assignments.views.assignment.common import (
    can_manage_assignment,
    get_assignment_by_id,
    validation_error_payload,
)


class AssignmentPublishAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def post(self, request, pk: int, *args, **kwargs):
        assignment = get_assignment_by_id(pk)
        if assignment is None:
            return Response(
                {"detail": "Работа не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not can_manage_assignment(request.user, assignment):
            return Response(
                {"detail": "Нет доступа."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            assignment = publish_assignment(assignment)
        except DjangoValidationError as exc:
            return Response(
                validation_error_payload(exc),
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AssignmentDetailSerializer(
            assignment,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class AssignmentArchiveAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def post(self, request, pk: int, *args, **kwargs):
        assignment = get_assignment_by_id(pk)
        if assignment is None:
            return Response(
                {"detail": "Работа не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not can_manage_assignment(request.user, assignment):
            return Response(
                {"detail": "Нет доступа."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            assignment = archive_assignment(assignment)
        except DjangoValidationError as exc:
            return Response(
                validation_error_payload(exc),
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AssignmentDetailSerializer(
            assignment,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class AssignmentDuplicateAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def post(self, request, pk: int, *args, **kwargs):
        assignment = get_assignment_by_id(pk)
        if assignment is None:
            return Response(
                {"detail": "Работа не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not can_manage_assignment(request.user, assignment):
            return Response(
                {"detail": "Нет доступа."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = AssignmentDuplicateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            duplicated = duplicate_assignment(
                source_assignment=assignment,
                author=request.user,
                title=serializer.validated_data.get("title")
                or f"Копия: {assignment.title}",
            )
        except DjangoValidationError as exc:
            return Response(
                validation_error_payload(exc),
                status=status.HTTP_400_BAD_REQUEST,
            )

        output_serializer = AssignmentDetailSerializer(
            duplicated,
            context={"request": request},
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
