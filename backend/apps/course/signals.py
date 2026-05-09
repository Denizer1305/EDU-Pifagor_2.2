from __future__ import annotations

from django.db.models import Sum
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone

from apps.course.models import (
    Course,
    CourseEnrollment,
    CourseLesson,
    CourseModule,
    CourseProgress,
    LessonProgress,
)


def _recalculate_module_minutes(module: CourseModule) -> None:
    total_minutes = (
        module.lessons.aggregate(total=Sum("estimated_minutes")).get("total") or 0
    )

    if module.estimated_minutes != total_minutes:
        module.estimated_minutes = total_minutes
        module.save(update_fields=["estimated_minutes", "updated_at"])


def _recalculate_course_minutes(course: Course) -> None:
    total_minutes = (
        course.lessons.filter(
            is_published=True,
            module__is_published=True,
        )
        .aggregate(total=Sum("estimated_minutes"))
        .get("total")
        or 0
    )

    if course.estimated_minutes != total_minutes:
        course.estimated_minutes = total_minutes
        course.save(update_fields=["estimated_minutes", "updated_at"])


@receiver(
    post_save,
    sender=CourseLesson,
    dispatch_uid="course_lesson_post_save_recalculate_minutes",
)
def course_lesson_post_save_recalculate_minutes(sender, instance, created, **kwargs):
    if kwargs.get("raw"):
        return

    _recalculate_module_minutes(instance.module)
    _recalculate_course_minutes(instance.course)


@receiver(
    post_delete,
    sender=CourseLesson,
    dispatch_uid="course_lesson_post_delete_recalculate_minutes",
)
def course_lesson_post_delete_recalculate_minutes(sender, instance, **kwargs):
    module = instance.module
    course = instance.course

    if module and CourseModule.objects.filter(pk=module.pk).exists():
        _recalculate_module_minutes(module)

    if course and Course.objects.filter(pk=course.pk).exists():
        _recalculate_course_minutes(course)


@receiver(
    post_save,
    sender=CourseModule,
    dispatch_uid="course_module_post_save_recalculate_course_minutes",
)
def course_module_post_save_recalculate_course_minutes(
    sender, instance, created, **kwargs
):
    if kwargs.get("raw"):
        return

    _recalculate_course_minutes(instance.course)


@receiver(
    post_delete,
    sender=CourseModule,
    dispatch_uid="course_module_post_delete_recalculate_course_minutes",
)
def course_module_post_delete_recalculate_course_minutes(sender, instance, **kwargs):
    course = instance.course
    if course and Course.objects.filter(pk=course.pk).exists():
        _recalculate_course_minutes(course)


@receiver(
    post_save,
    sender=CourseEnrollment,
    dispatch_uid="course_enrollment_post_save_ensure_progress",
)
def course_enrollment_post_save_ensure_progress(sender, instance, created, **kwargs):
    if kwargs.get("raw"):
        return

    if created:
        CourseProgress.objects.get_or_create(enrollment=instance)


@receiver(
    post_save,
    sender=LessonProgress,
    dispatch_uid="lesson_progress_post_save_recalculate_course_progress",
)
def lesson_progress_post_save_recalculate_course_progress(
    sender, instance, created, **kwargs
):
    if kwargs.get("raw"):
        return

    from apps.course.services.course_progress_services import (
        recalculate_course_progress,
    )

    recalculate_course_progress(
        enrollment=instance.enrollment,
        last_lesson=instance.lesson,
    )


@receiver(
    post_delete,
    sender=LessonProgress,
    dispatch_uid="lesson_progress_post_delete_recalculate_course_progress",
)
def lesson_progress_post_delete_recalculate_course_progress(sender, instance, **kwargs):
    if not instance.enrollment_id:
        return

    from apps.course.services.course_progress_services import (
        recalculate_course_progress,
    )

    recalculate_course_progress(
        enrollment=instance.enrollment,
        last_lesson=None,
    )


@receiver(
    post_save, sender=Course, dispatch_uid="course_post_save_sync_publish_archive_dates"
)
def course_post_save_sync_publish_archive_dates(sender, instance, created, **kwargs):
    if kwargs.get("raw"):
        return

    update_fields: list[str] = []

    if (
        instance.status == Course.StatusChoices.PUBLISHED
        and instance.published_at is None
    ):
        instance.published_at = timezone.now()
        update_fields.append("published_at")

    if (
        instance.status == Course.StatusChoices.ARCHIVED
        and instance.archived_at is None
    ):
        instance.archived_at = timezone.now()
        update_fields.append("archived_at")

    if update_fields:
        instance.save(update_fields=[*update_fields, "updated_at"])
