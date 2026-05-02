from __future__ import annotations

from apps.assignments.tests.factories.users import (
    create_student_user,
    create_teacher_user,
)
from apps.course.tests.factories import (
    create_course as base_create_course,
)
from apps.course.tests.factories import (
    create_course_enrollment as base_create_course_enrollment,
)
from apps.course.tests.factories import (
    create_course_lesson as base_create_course_lesson,
)
from apps.education.tests.factories import (
    create_student_group_enrollment as base_create_student_group_enrollment,
)


def create_course(author=None, **kwargs):
    """Создаёт тестовый курс."""

    author = author or create_teacher_user()
    return base_create_course(author=author, **kwargs)


def create_course_lesson(course=None, **kwargs):
    """Создаёт тестовый урок курса."""

    course = course or create_course()
    return base_create_course_lesson(course=course, **kwargs)


def create_course_enrollment(course=None, student=None, **kwargs):
    """Создаёт тестовое зачисление студента на курс."""

    course = course or create_course()
    student = student or create_student_user()
    return base_create_course_enrollment(course=course, student=student, **kwargs)


def create_group_with_enrollment(student=None, **kwargs):
    """Создаёт учебную группу и зачисление студента в неё."""

    student = student or create_student_user()
    enrollment = base_create_student_group_enrollment(student=student, **kwargs)
    return enrollment.group, enrollment
