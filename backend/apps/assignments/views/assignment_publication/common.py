from __future__ import annotations

from django.apps import apps
from django.core.exceptions import ValidationError as DjangoValidationError

from apps.assignments.models import Assignment, AssignmentPublication
from apps.assignments.permissions import is_admin


def parse_bool(value):
    """Преобразует query-параметр в bool или None."""

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


def validation_error_payload(exc: DjangoValidationError):
    """Преобразует Django ValidationError в payload для DRF Response."""

    if hasattr(exc, "message_dict"):
        return exc.message_dict

    if hasattr(exc, "messages"):
        return {"detail": exc.messages}

    return {"detail": str(exc)}


def get_course_by_id(course_id):
    """Возвращает курс по id или None."""

    if not course_id:
        return None

    Course = apps.get_model("course", "Course")
    return Course.objects.filter(id=course_id).first()


def get_lesson_by_id(lesson_id):
    """Возвращает урок курса по id или None."""

    if not lesson_id:
        return None

    CourseLesson = apps.get_model("course", "CourseLesson")
    return CourseLesson.objects.filter(id=lesson_id).first()


def get_assignment_by_id(assignment_id):
    """Возвращает работу по id или None."""

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


def get_publication_by_id(publication_id):
    """Возвращает публикацию работы по id или None."""

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


def can_manage_publication(user, publication: AssignmentPublication) -> bool:
    """Проверяет, может ли пользователь управлять публикацией."""

    if not user or not user.is_authenticated:
        return False

    if is_admin(user):
        return True

    assignment = getattr(publication, "assignment", None)
    return bool(assignment and assignment.author_id == user.id)


def can_manage_assignment(user, assignment: Assignment) -> bool:
    """Проверяет, может ли пользователь управлять работой."""

    if not user or not user.is_authenticated:
        return False

    if is_admin(user):
        return True

    return assignment.author_id == user.id


def get_publication_queryset_for_user(user):
    """Возвращает queryset публикаций, доступных текущему пользователю."""

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
