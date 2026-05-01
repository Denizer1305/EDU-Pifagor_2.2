from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assignments.permissions import IsTeacherOrAdmin
from apps.assignments.serializers import AssignmentPublicationDetailSerializer
from apps.assignments.services import (
    archive_assignment_publication,
    close_assignment_publication,
    publish_assignment_publication,
)
from apps.assignments.views.assignment_publication.common import (
    can_manage_publication,
    get_publication_by_id,
    validation_error_payload,
)


class AssignmentPublicationPublishAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def post(self, request, pk: int, *args, **kwargs):
        publication = get_publication_by_id(pk)
        if publication is None:
            return Response(
                {"detail": "Публикация не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not can_manage_publication(request.user, publication):
            return Response(
                {"detail": "Нет доступа."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            publication = publish_assignment_publication(publication)
        except DjangoValidationError as exc:
            return Response(
                validation_error_payload(exc),
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AssignmentPublicationDetailSerializer(
            publication,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class AssignmentPublicationCloseAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def post(self, request, pk: int, *args, **kwargs):
        publication = get_publication_by_id(pk)
        if publication is None:
            return Response(
                {"detail": "Публикация не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not can_manage_publication(request.user, publication):
            return Response(
                {"detail": "Нет доступа."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            publication = close_assignment_publication(publication)
        except DjangoValidationError as exc:
            return Response(
                validation_error_payload(exc),
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AssignmentPublicationDetailSerializer(
            publication,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class AssignmentPublicationArchiveAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def post(self, request, pk: int, *args, **kwargs):
        publication = get_publication_by_id(pk)
        if publication is None:
            return Response(
                {"detail": "Публикация не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not can_manage_publication(request.user, publication):
            return Response(
                {"detail": "Нет доступа."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            publication = archive_assignment_publication(publication)
        except DjangoValidationError as exc:
            return Response(
                validation_error_payload(exc),
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AssignmentPublicationDetailSerializer(
            publication,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
