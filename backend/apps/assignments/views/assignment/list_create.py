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
    AssignmentCreateSerializer,
    AssignmentDetailSerializer,
    AssignmentListSerializer,
)
from apps.assignments.services import create_assignment
from apps.assignments.views.assignment.common import (
    get_assignment_queryset_for_user,
    get_course_by_id,
    get_lesson_by_id,
    parse_bool,
    validation_error_payload,
)

logger = logging.getLogger(__name__)


class AssignmentListCreateAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def get(self, request, *args, **kwargs):
        logger.info(
            "AssignmentListCreateAPIView.get called user_id=%s",
            request.user.id,
        )

        queryset = get_assignment_queryset_for_user(request.user)

        search = (request.query_params.get("search") or "").strip()
        status_value = (request.query_params.get("status") or "").strip()
        assignment_kind = (request.query_params.get("assignment_kind") or "").strip()
        control_scope = (request.query_params.get("control_scope") or "").strip()
        course_id = request.query_params.get("course_id")
        lesson_id = request.query_params.get("lesson_id")
        is_active = parse_bool(request.query_params.get("is_active"))

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(subtitle__icontains=search)
                | Q(description__icontains=search)
                | Q(instructions__icontains=search)
            )

        if status_value:
            queryset = queryset.filter(status=status_value)

        if assignment_kind:
            queryset = queryset.filter(assignment_kind=assignment_kind)

        if control_scope:
            queryset = queryset.filter(control_scope=control_scope)

        if course_id:
            queryset = queryset.filter(course_id=course_id)

        if lesson_id:
            queryset = queryset.filter(lesson_id=lesson_id)

        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)

        serializer = AssignmentListSerializer(
            queryset,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        logger.info(
            "AssignmentListCreateAPIView.post called user_id=%s",
            request.user.id,
        )

        serializer = AssignmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated = serializer.validated_data

        course = get_course_by_id(validated.get("course_id"))
        if validated.get("course_id") and course is None:
            return Response(
                {"detail": "Курс не найден."},
                status=status.HTTP_404_NOT_FOUND,
            )

        lesson = get_lesson_by_id(validated.get("lesson_id"))
        if validated.get("lesson_id") and lesson is None:
            return Response(
                {"detail": "Урок не найден."},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            assignment = create_assignment(
                author=request.user,
                title=validated["title"],
                subtitle=validated.get("subtitle", ""),
                description=validated.get("description", ""),
                instructions=validated.get("instructions", ""),
                assignment_kind=validated.get("assignment_kind", ""),
                control_scope=validated.get("control_scope", ""),
                visibility=validated.get("visibility", ""),
                education_level=validated.get("education_level", ""),
                is_template=validated.get("is_template", False),
                is_active=validated.get("is_active", True),
                course=course,
                lesson=lesson,
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
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
