from __future__ import annotations

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assignments.permissions import IsTeacherOrAdmin
from apps.assignments.serializers import (
    AssignmentDetailSerializer,
    AssignmentUpdateSerializer,
)
from apps.assignments.services import update_assignment
from apps.assignments.views.assignment.common import (
    can_manage_assignment,
    get_assignment_by_id,
    get_course_by_id,
    get_lesson_by_id,
    validation_error_payload,
)


class AssignmentDetailAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def get_object(self, pk: int):
        return get_assignment_by_id(pk)

    def get(self, request, pk: int, *args, **kwargs):
        assignment = self.get_object(pk)
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

        serializer = AssignmentDetailSerializer(
            assignment,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk: int, *args, **kwargs):
        assignment = self.get_object(pk)
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

        serializer = AssignmentUpdateSerializer(
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
            assignment = update_assignment(
                assignment,
                **validated,
            )
        except DjangoValidationError as exc:
            return Response(
                validation_error_payload(exc),
                status=status.HTTP_400_BAD_REQUEST,
            )

        output_serializer = AssignmentDetailSerializer(
            assignment,
            context={"request": request},
        )
        return Response(output_serializer.data, status=status.HTTP_200_OK)
