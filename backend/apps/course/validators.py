from __future__ import annotations

from django.core.exceptions import ValidationError

from apps.course.models import Course, CourseAssignment, CourseEnrollment
from apps.users.constants import ROLE_ADMIN, ROLE_STUDENT, ROLE_TEACHER


def _get_user_role_codes(user) -> set[str]:
    if not user or not user.is_authenticated:
        return set()

    if user.is_superuser:
        return {ROLE_ADMIN}

    if not hasattr(user, "user_roles"):
        return set()

    queryset = user.user_roles.all()
    model_fields = {field.name for field in queryset.model._meta.get_fields()}

    if "is_active" in model_fields:
        queryset = queryset.filter(is_active=True)

    return set(queryset.values_list("role__code", flat=True))


def is_admin_user(user) -> bool:
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    return ROLE_ADMIN in _get_user_role_codes(user)


def is_teacher_user(user) -> bool:
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    role_codes = _get_user_role_codes(user)
    return (
        ROLE_TEACHER in role_codes
        or getattr(user, "registration_type", "") == "teacher"
    )


def is_student_user(user) -> bool:
    if not user or not user.is_authenticated:
        return False

    role_codes = _get_user_role_codes(user)
    return (
        ROLE_STUDENT in role_codes
        or getattr(user, "registration_type", "") == "student"
    )


def validate_course_dates(*, starts_at=None, ends_at=None) -> None:
    if starts_at and ends_at and ends_at < starts_at:
        raise ValidationError(
            {"ends_at": "Дата окончания курса не может быть раньше даты начала."}
        )


def validate_course_teacher_user(*, user) -> None:
    if not is_teacher_user(user) and not is_admin_user(user):
        raise ValidationError(
            {
                "teacher": "Преподавателем курса может быть только преподаватель или администратор."
            }
        )


def validate_course_student_user(*, user) -> None:
    if not is_student_user(user) and not is_admin_user(user):
        raise ValidationError(
            {"student": "Запись на курс доступна только для студента."}
        )


def validate_module_belongs_to_course(*, module, course) -> None:
    if module.course_id != course.id:
        raise ValidationError(
            {"module": "Модуль должен принадлежать выбранному курсу."}
        )


def validate_lesson_belongs_to_course(*, lesson, course) -> None:
    if lesson.course_id != course.id:
        raise ValidationError({"lesson": "Урок должен принадлежать выбранному курсу."})


def validate_course_can_be_published(*, course: Course) -> None:
    errors = {}

    if not course.title:
        errors["title"] = "Нельзя публиковать курс без названия."

    if not course.modules.exists():
        errors["modules"] = "Нельзя публиковать курс без модулей."

    if not course.lessons.filter(
        is_published=True,
        module__is_published=True,
    ).exists():
        errors["lessons"] = "Нельзя публиковать курс без опубликованных уроков."

    if errors:
        raise ValidationError(errors)


def validate_assignment_payload(
    *,
    assignment_type: str,
    group=None,
    student=None,
    starts_at=None,
    ends_at=None,
) -> None:
    errors = {}

    if starts_at and ends_at and ends_at < starts_at:
        errors["ends_at"] = (
            "Дата окончания назначения не может быть раньше даты начала."
        )

    if assignment_type == CourseAssignment.AssignmentTypeChoices.GROUP:
        if group is None:
            errors["group"] = "Для группового назначения нужно указать группу."
        if student is not None:
            errors["student"] = "Для группового назначения нельзя указывать студента."

    if assignment_type == CourseAssignment.AssignmentTypeChoices.STUDENT:
        if student is None:
            errors["student"] = "Для персонального назначения нужно указать студента."
        if group is not None:
            errors["group"] = "Для персонального назначения нельзя указывать группу."

    if errors:
        raise ValidationError(errors)


def validate_enrollment_payload(
    *,
    course: Course,
    student,
    assignment=None,
) -> None:
    errors = {}

    validate_course_student_user(user=student)

    if course.status == Course.StatusChoices.ARCHIVED:
        errors["course"] = "Нельзя записать пользователя на архивный курс."

    if assignment is not None and assignment.course_id != course.id:
        errors["assignment"] = "Назначение должно относиться к этому же курсу."

    if errors:
        raise ValidationError(errors)


def validate_progress_percent(value: int) -> None:
    if value < 0 or value > 100:
        raise ValidationError(
            {"progress_percent": "Прогресс должен быть в диапазоне от 0 до 100."}
        )


def validate_course_completion_state(*, enrollment: CourseEnrollment) -> None:
    if (
        enrollment.status == CourseEnrollment.StatusChoices.COMPLETED
        and enrollment.completed_at is None
    ):
        raise ValidationError(
            {"completed_at": "Для завершённого курса нужна дата завершения."}
        )
