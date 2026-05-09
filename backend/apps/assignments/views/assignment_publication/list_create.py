from __future__ import annotations

import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assignments.permissions import IsTeacherOrAdmin
from apps.assignments.serializers import (
    AssignmentPublicationCreateSerializer,
    AssignmentPublicationDetailSerializer,
    AssignmentPublicationListSerializer,
)
from apps.assignments.services import create_assignment_publication
from apps.assignments.views.assignment_publication.common import (
    can_manage_assignment,
    get_assignment_by_id,
    get_course_by_id,
    get_lesson_by_id,
    get_publication_queryset_for_user,
    parse_bool,
    validation_error_payload,
)

logger = logging.getLogger(__name__)


class AssignmentPublicationListCreateAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def get(self, request, *args, **kwargs):
        logger.info(
            "AssignmentPublicationListCreateAPIView.get called user_id=%s",
            request.user.id,
        )

        queryset = get_publication_queryset_for_user(request.user)

        search = (request.query_params.get("search") or "").strip()
        status_value = (request.query_params.get("status") or "").strip()
        assignment_id = request.query_params.get("assignment_id")
        course_id = request.query_params.get("course_id")
        lesson_id = request.query_params.get("lesson_id")
        is_active = parse_bool(request.query_params.get("is_active"))

        if search:
            queryset = queryset.filter(
                Q(title_override__icontains=search)
                | Q(notes__icontains=search)
                | Q(assignment__title__icontains=search)
            )

        if status_value:
            queryset = queryset.filter(status=status_value)

        if assignment_id:
            queryset = queryset.filter(assignment_id=assignment_id)

        if course_id:
            queryset = queryset.filter(course_id=course_id)

        if lesson_id:
            queryset = queryset.filter(lesson_id=lesson_id)

        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)

        serializer = AssignmentPublicationListSerializer(
            queryset,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        logger.info(
            "AssignmentPublicationListCreateAPIView.post called user_id=%s",
            request.user.id,
        )

        serializer = AssignmentPublicationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        assignment = get_assignment_by_id(validated.get("assignment_id"))
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

        course = assignment.course
        if "course_id" in validated:
            course = get_course_by_id(validated.get("course_id"))

            if validated.get("course_id") and course is None:
                return Response(
                    {"detail": "Курс не найден."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        lesson = assignment.lesson
        if "lesson_id" in validated:
            lesson = get_lesson_by_id(validated.get("lesson_id"))

            if validated.get("lesson_id") and lesson is None:
                return Response(
                    {"detail": "Урок не найден."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        try:
            publication = create_assignment_publication(
                assignment=assignment,
                course=course,
                lesson=lesson,
                published_by=request.user,
                title_override=validated.get("title_override", ""),
                starts_at=validated.get("starts_at"),
                due_at=validated.get("due_at"),
                available_until=validated.get("available_until"),
                notes=validated.get("notes", ""),
                is_active=validated.get("is_active", True),
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
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
