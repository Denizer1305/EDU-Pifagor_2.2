from __future__ import annotations

from django.db.models import Prefetch

from apps.course.models import Course, CourseLesson, CourseMaterial, CourseModule


def get_course_structure_queryset():
    lessons_queryset = (
        CourseLesson.objects.select_related("module")
        .prefetch_related(
            Prefetch(
                "materials",
                queryset=CourseMaterial.objects.order_by("order", "id"),
            )
        )
        .order_by("order", "id")
    )

    modules_queryset = CourseModule.objects.prefetch_related(
        Prefetch("lessons", queryset=lessons_queryset)
    ).order_by("order", "id")

    return Course.objects.prefetch_related(
        Prefetch("modules", queryset=modules_queryset),
        Prefetch(
            "materials",
            queryset=CourseMaterial.objects.filter(lesson__isnull=True).order_by(
                "order", "id"
            ),
        ),
    ).select_related(
        "author",
        "organization",
        "subject",
        "academic_year",
        "period",
        "group_subject",
    )


def get_course_module_by_id(*, module_id: int):
    return (
        CourseModule.objects.select_related("course")
        .prefetch_related(
            Prefetch(
                "lessons",
                queryset=CourseLesson.objects.order_by("order", "id"),
            )
        )
        .filter(id=module_id)
        .first()
    )


def get_course_lesson_by_id(*, lesson_id: int):
    return (
        CourseLesson.objects.select_related(
            "course",
            "module",
        )
        .prefetch_related(
            Prefetch(
                "materials",
                queryset=CourseMaterial.objects.order_by("order", "id"),
            )
        )
        .filter(id=lesson_id)
        .first()
    )


def get_course_material_queryset(
    *, course_id: int | None = None, lesson_id: int | None = None
):
    queryset = CourseMaterial.objects.select_related(
        "course",
        "lesson",
    )

    if course_id:
        queryset = queryset.filter(course_id=course_id)

    if lesson_id:
        queryset = queryset.filter(lesson_id=lesson_id)

    return queryset.order_by("order", "id")
