from __future__ import annotations

import logging

from django.apps import apps
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assignments.permissions import IsTeacherOrAdmin
from apps.assignments.serializers import (
    AssignmentAudienceCreateSerializer,
    AssignmentAudienceSerializer,
)
from apps.assignments.selectors import (
    get_assignment_audiences_queryset,
    get_assignment_publication_by_id,
)
from apps.assignments.services import (
    assign_publication_to_course_enrollment,
    assign_publication_to_student,
)

logger = logging.getLogger(__name__)


class AssignmentAudienceListCreateAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def get(self, request, publication_id: int, *args, **kwargs):
        publication = get_assignment_publication_by_id(publication_id=publication_id)
        if publication is None:
            return Response(
                {"detail": "Публикация не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        queryset = get_assignment_audiences_queryset(publication_id=publication.id)
        serializer = AssignmentAudienceSerializer(
            queryset,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, publication_id: int, *args, **kwargs):
        publication = get_assignment_publication_by_id(publication_id=publication_id)
        if publication is None:
            return Response(
                {"detail": "Публикация не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AssignmentAudienceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        audience_type = (validated.get("audience_type") or "").strip()

        if validated.get("course_enrollment_id"):
            CourseEnrollment = apps.get_model("course", "CourseEnrollment")
            enrollment = CourseEnrollment.objects.filter(
                id=validated["course_enrollment_id"]
            ).first()
            if enrollment is None:
                return Response(
                    {"detail": "Запись на курс не найдена."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            audience = assign_publication_to_course_enrollment(
                publication=publication,
                course_enrollment=enrollment,
                is_active=validated.get("is_active", True),
            )
        elif audience_type in {"student", "selected_students"}:
            User = apps.get_model("users", "User")
            student = User.objects.filter(id=validated.get("student_id")).first()
            if student is None:
                return Response(
                    {"detail": "Студент не найден."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            audience = assign_publication_to_student(
                publication=publication,
                student=student,
                audience_type=audience_type,
                is_active=validated.get("is_active", True),
            )
        else:
            return Response(
                {"detail": "Пока поддерживается назначение на студента или запись на курс."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        output = AssignmentAudienceSerializer(
            audience,
            context={"request": request},
        )
        return Response(output.data, status=status.HTTP_201_CREATED)
