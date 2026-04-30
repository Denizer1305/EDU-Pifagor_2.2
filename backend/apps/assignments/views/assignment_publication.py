from __future__ import annotations

import logging

from django.apps import apps
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.assignments.models import Assignment, AssignmentPublication
from apps.assignments.permissions import IsTeacherOrAdmin, is_admin
from apps.assignments.serializers import (
    AssignmentPublicationCreateSerializer,
    AssignmentPublicationDetailSerializer,
    AssignmentPublicationListSerializer,
    AssignmentPublicationUpdateSerializer,
)
from apps.assignments.services import (
    archive_assignment_publication,
    close_assignment_publication,
    create_assignment_publication,
    publish_assignment_publication,
    update_assignment_publication,
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


def _get_publication_by_id(publication_id):
    if not publication_id:
        return None

    return (
        AssignmentPublication.objects.select_related(
            "assignment",
            "assignment__author",
            "course",
            "lesson",
            "published_by",
        )
        .filter(id=publication_id)
        .first()
    )


def _can_manage_publication(user, publication: AssignmentPublication) -> bool:
    if not user or not user.is_authenticated:
        return False

    if is_admin(user):
        return True

    assignment = getattr(publication, "assignment", None)
    return bool(assignment and assignment.author_id == user.id)


def _can_manage_assignment(user, assignment: Assignment) -> bool:
    if not user or not user.is_authenticated:
        return False

    if is_admin(user):
        return True

    return assignment.author_id == user.id


def _get_publication_queryset_for_user(user):
    queryset = AssignmentPublication.objects.select_related(
        "assignment",
        "assignment__author",
        "course",
        "lesson",
        "published_by",
    ).all()

    if not is_admin(user):
        queryset = queryset.filter(assignment__author=user)

    return queryset.order_by("-created_at", "-id")


class AssignmentPublicationListCreateAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def get(self, request, *args, **kwargs):
        logger.info(
            "AssignmentPublicationListCreateAPIView.get called user_id=%s",
            request.user.id,
        )

        queryset = _get_publication_queryset_for_user(request.user)

        search = (request.query_params.get("search") or "").strip()
        status_value = (request.query_params.get("status") or "").strip()
        assignment_id = request.query_params.get("assignment_id")
        course_id = request.query_params.get("course_id")
        lesson_id = request.query_params.get("lesson_id")
        is_active = _parse_bool(request.query_params.get("is_active"))

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

        assignment = _get_assignment_by_id(validated.get("assignment_id"))
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

        course = assignment.course
        if "course_id" in validated:
            course = _get_course_by_id(validated.get("course_id"))

            if validated.get("course_id") and course is None:
                return Response(
                    {"detail": "Курс не найден."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        lesson = assignment.lesson
        if "lesson_id" in validated:
            lesson = _get_lesson_by_id(validated.get("lesson_id"))

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
                _validation_error_payload(exc),
                status=status.HTTP_400_BAD_REQUEST,
            )

        output_serializer = AssignmentPublicationDetailSerializer(
            publication,
            context={"request": request},
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class AssignmentPublicationDetailAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def get_object(self, pk: int):
        return _get_publication_by_id(pk)

    def get(self, request, pk: int, *args, **kwargs):
        publication = self.get_object(pk)
        if publication is None:
            return Response(
                {"detail": "Публикация не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not _can_manage_publication(request.user, publication):
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

        if not _can_manage_publication(request.user, publication):
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
            publication = update_assignment_publication(
                publication,
                **validated,
            )
        except DjangoValidationError as exc:
            return Response(
                _validation_error_payload(exc),
                status=status.HTTP_400_BAD_REQUEST,
            )

        output_serializer = AssignmentPublicationDetailSerializer(
            publication,
            context={"request": request},
        )
        return Response(output_serializer.data, status=status.HTTP_200_OK)


class AssignmentPublicationPublishAPIView(APIView):
    permission_classes = (IsAuthenticated, IsTeacherOrAdmin)

    def post(self, request, pk: int, *args, **kwargs):
        publication = _get_publication_by_id(pk)
        if publication is None:
            return Response(
                {"detail": "Публикация не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not _can_manage_publication(request.user, publication):
            return Response(
                {"detail": "Нет доступа."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            publication = publish_assignment_publication(publication)
        except DjangoValidationError as exc:
            return Response(
                _validation_error_payload(exc),
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
        publication = _get_publication_by_id(pk)
        if publication is None:
            return Response(
                {"detail": "Публикация не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not _can_manage_publication(request.user, publication):
            return Response(
                {"detail": "Нет доступа."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            publication = close_assignment_publication(publication)
        except DjangoValidationError as exc:
            return Response(
                _validation_error_payload(exc),
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
        publication = _get_publication_by_id(pk)
        if publication is None:
            return Response(
                {"detail": "Публикация не найдена."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not _can_manage_publication(request.user, publication):
            return Response(
                {"detail": "Нет доступа."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            publication = archive_assignment_publication(publication)
        except DjangoValidationError as exc:
            return Response(
                _validation_error_payload(exc),
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AssignmentPublicationDetailSerializer(
            publication,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
