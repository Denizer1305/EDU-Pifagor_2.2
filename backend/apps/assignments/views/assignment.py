from __future__ import annotations

import logging

from django.apps import apps
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assignments.models import Assignment
from apps.assignments.permissions import IsTeacherOrAdmin, is_admin
from apps.assignments.serializers import (
    AssignmentCreateSerializer,
    AssignmentDetailSerializer,
    AssignmentDuplicateSerializer,
    AssignmentListSerializer,
    AssignmentUpdateSerializer,
)
from apps.assignments.services import (
    archive_assignment,
    create_assignment,
    duplicate_assignment,
    publish_assignment,
    update_assignment,
)

logger = logging.getLogger(__name__)


def _parse_bool(value):
    if value in (None, ""):
        return None

    if isinstance(value, bool):
        return value

    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes", "y", "on"}:
        return True
    if normalized in {"false", "0", "no", "n", "off"}:
        return False

    return None


def _validation_error_payload(exc: DjangoValidationError):
    if hasattr(exc, "message_dict"):
        return exc.message_dict
    if hasattr(exc, "messages"):
        return {"detail": exc.messages}
    return {"detail": str(exc)}


def _get_course_by_id(course_id):
    if not course_id:
        return None

    Course = apps.get_model("course", "Course")
    return Course.objects.filter(id=course_id).first()


def _get_lesson_by_id(lesson_id):
    if not lesson_id:
        return None

    CourseLesson = apps.get_model("course", "CourseLesson")
    return CourseLesson.objects.filter(id=lesson_id).first()


def _get_assignment_by_id(assignment_id):
    if not assignment_id:
        return None

    return (
        Assignment.objects.select_related(
            "author",
            "course",
            "lesson",
        )
        .filter(id=assignment_id)
        .first()
    )


def _can_manage_assignment(user, assignment: Assignment) -> bool:
    if not user or not user.is_authenticated:
        return False

    if is_admin(user):
        return True

    return assignment.author_id == user.id


def _get_assignment_queryset_for_user(user):
    queryset = Assignment.objects.select_related(
        "author",
        "course",
        "lesson",
    ).all()

    if not is_admin(user):
        queryset = queryset.filter(author=user)

    return queryset.order_by("-created_at", "-id")


class AssignmentListCreateAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def get(self, request, *args, **kwargs):
        logger.info(
            "AssignmentListCreateAPIView.get called user_id=%s",
            request.user.id,
        )

        queryset = _get_assignment_queryset_for_user(request.user)

        search = (request.query_params.get("search") or "").strip()
        status_value = (request.query_params.get("status") or "").strip()
        assignment_kind = (request.query_params.get("assignment_kind") or "").strip()
        control_scope = (request.query_params.get("control_scope") or "").strip()
        course_id = request.query_params.get("course_id")
        lesson_id = request.query_params.get("lesson_id")
        is_active = _parse_bool(request.query_params.get("is_active"))

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

        course = _get_course_by_id(validated.get("course_id"))
        if validated.get("course_id") and course is None:
            return Response(
                {"detail": "Курс не найден."},
                status=status.HTTP_404_NOT_FOUND,
            )

        lesson = _get_lesson_by_id(validated.get("lesson_id"))
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
                _validation_error_payload(exc),
                status=status.HTTP_400_BAD_REQUEST,
            )

        output_serializer = AssignmentDetailSerializer(
            assignment,
            context={"request": request},
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class AssignmentDetailAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def get_object(self, pk: int):
        return _get_assignment_by_id(pk)

    def get(self, request, pk: int, *args, **kwargs):
        assignment = self.get_object(pk)
        if assignment is None:
            return Response(
                {"detail": "Работа не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not _can_manage_assignment(request.user, assignment):
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

        if not _can_manage_assignment(request.user, assignment):
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
            course = _get_course_by_id(course_id)

            if course_id and course is None:
                return Response(
                    {"detail": "Курс не найден."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            validated["course"] = course

        if "lesson_id" in validated:
            lesson_id = validated.pop("lesson_id")
            lesson = _get_lesson_by_id(lesson_id)

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
                _validation_error_payload(exc),
                status=status.HTTP_400_BAD_REQUEST,
            )

        output_serializer = AssignmentDetailSerializer(
            assignment,
            context={"request": request},
        )
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class AssignmentPublishAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def post(self, request, pk: int, *args, **kwargs):
        assignment = _get_assignment_by_id(pk)
        if assignment is None:
            return Response(
                {"detail": "Работа не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not _can_manage_assignment(request.user, assignment):
            return Response(
                {"detail": "Нет доступа."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            assignment = publish_assignment(assignment)
        except DjangoValidationError as exc:
            return Response(
                _validation_error_payload(exc),
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
        assignment = _get_assignment_by_id(pk)
        if assignment is None:
            return Response(
                {"detail": "Работа не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not _can_manage_assignment(request.user, assignment):
            return Response(
                {"detail": "Нет доступа."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            assignment = archive_assignment(assignment)
        except DjangoValidationError as exc:
            return Response(
                _validation_error_payload(exc),
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
        assignment = _get_assignment_by_id(pk)
        if assignment is None:
            return Response(
                {"detail": "Работа не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not _can_manage_assignment(request.user, assignment):
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
                _validation_error_payload(exc),
                status=status.HTTP_400_BAD_REQUEST,
            )

        output_serializer = AssignmentDetailSerializer(
            duplicated,
            context={"request": request},
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
