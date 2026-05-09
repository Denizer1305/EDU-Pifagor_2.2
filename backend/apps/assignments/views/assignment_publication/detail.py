from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assignments.permissions import IsTeacherOrAdmin
from apps.assignments.serializers import (
    AssignmentPublicationDetailSerializer,
    AssignmentPublicationUpdateSerializer,
)
from apps.assignments.services import update_assignment_publication
from apps.assignments.views.assignment_publication.common import (
    can_manage_publication,
    get_course_by_id,
    get_lesson_by_id,
    get_publication_by_id,
    validation_error_payload,
)


class AssignmentPublicationDetailAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def get_object(self, pk: int):
        return get_publication_by_id(pk)

    def get(self, request, pk: int, *args, **kwargs):
        publication = self.get_object(pk)
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

        serializer = AssignmentPublicationDetailSerializer(
            publication,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk: int, *args, **kwargs):
        publication = self.get_object(pk)
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

        serializer = AssignmentPublicationUpdateSerializer(
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data.copy()

        if "course_id" in validated:
            course_id = validated.pop("course_id")
            course = get_course_by_id(course_id)

            if course_id and course is None:
                return Response(
                    {"detail": "Курс не найден."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            validated["course"] = course

        if "lesson_id" in validated:
            lesson_id = validated.pop("lesson_id")
            lesson = get_lesson_by_id(lesson_id)

            if lesson_id and lesson is None:
                return Response(
                    {"detail": "Урок не найден."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            validated["lesson"] = lesson

        try:
            publication = update_assignment_publication(
                publication,
                **validated,
            )
        except DjangoValidationError as exc:
            return Response(
                validation_error_payload(exc),
                status=status.HTTP_400_BAD_REQUEST,
            )

        output_serializer = AssignmentPublicationDetailSerializer(
            publication,
            context={"request": request},
        )
        return Response(output_serializer.data, status=status.HTTP_200_OK)
