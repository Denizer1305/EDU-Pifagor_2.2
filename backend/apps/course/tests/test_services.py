from __future__ import annotations

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.course.models import Course, CourseEnrollment, CourseTeacher, LessonProgress
from apps.course.services import (
    add_teacher_to_course,
    archive_course,
    assign_course_to_group,
    assign_course_to_student,
    cancel_course_enrollment,
    create_course,
    create_course_enrollment,
    create_course_lesson,
    create_course_material,
    create_course_module,
    duplicate_course,
    mark_lesson_completed,
    mark_lesson_in_progress,
    move_course_lesson,
    publish_course,
    recalculate_course_progress,
    remove_course_assignment,
    remove_teacher_from_course,
    reorder_course_lessons,
    reorder_course_modules,
    start_course_enrollment,
    update_course,
)
from apps.course.tests.factories import (
    create_course as create_course_factory,
    create_course_author,
    create_course_enrollment as create_course_enrollment_factory,
    create_course_file,
    create_course_lesson as create_course_lesson_factory,
    create_course_material as create_course_material_factory,
    create_course_module as create_course_module_factory,
    create_course_student,
    create_course_with_context,
)


class CourseServicesTestCase(TestCase):
    def test_create_course_creates_owner_link(self):
        author = create_course_author()
        course = create_course(
            author=author,
            title="Авторский курс",
        )

        self.assertEqual(course.author, author)
        self.assertTrue(
            CourseTeacher.objects.filter(
                course=course,
                teacher=author,
                role=CourseTeacher.RoleChoices.OWNER,
            ).exists()
        )

    def test_update_course_updates_title_and_slug(self):
        course = create_course_factory(title="Старое название")
        old_slug = course.slug

        updated = update_course(
            course=course,
            title="Новое название курса",
        )

        self.assertEqual(updated.title, "Новое название курса")
        self.assertTrue(updated.slug)
        self.assertNotEqual(updated.slug, "")

    def test_publish_course_requires_structure(self):
        course = create_course_factory()

        with self.assertRaises(ValidationError):
            publish_course(course=course)

    def test_publish_course_with_structure(self):
        course = create_course_factory()
        module = create_course_module_factory(course=course)
        create_course_lesson_factory(course=course, module=module)

        updated = publish_course(course=course)

        self.assertEqual(updated.status, Course.StatusChoices.PUBLISHED)
        self.assertIsNotNone(updated.published_at)

    def test_archive_course(self):
        course = create_course_factory(status=Course.StatusChoices.PUBLISHED)

        updated = archive_course(course=course)

        self.assertEqual(updated.status, Course.StatusChoices.ARCHIVED)
        self.assertFalse(updated.is_active)

    def test_duplicate_course_copies_structure(self):
        course = create_course_factory()
        module = create_course_module_factory(course=course, title="Модуль 1")
        lesson = create_course_lesson_factory(course=course, module=module, title="Урок 1")
        create_course_material_factory(course=course, lesson=lesson, title="Файл 1")

        new_author = create_course_author()
        new_course = duplicate_course(
            source_course=course,
            author=new_author,
            title="Копия курса",
        )

        self.assertEqual(new_course.title, "Копия курса")
        self.assertEqual(new_course.modules.count(), 1)
        self.assertEqual(new_course.lessons.count(), 1)
        self.assertEqual(new_course.materials.count(), 1)

    def test_add_and_remove_teacher_from_course(self):
        course = create_course_factory()
        teacher = create_course_author()

        link = add_teacher_to_course(
            course=course,
            teacher=teacher,
        )
        self.assertEqual(link.teacher, teacher)

        remove_teacher_from_course(course=course, teacher=teacher)
        link.refresh_from_db()
        self.assertFalse(link.is_active)


class CourseStructureServicesTestCase(TestCase):
    def test_create_course_module(self):
        course = create_course_factory()

        module = create_course_module(
            course=course,
            title="Раздел 1",
        )

        self.assertEqual(module.course, course)
        self.assertEqual(module.title, "Раздел 1")

    def test_reorder_course_modules(self):
        course = create_course_factory()
        first = create_course_module_factory(course=course, order=1, title="Первый")
        second = create_course_module_factory(course=course, order=2, title="Второй")

        reorder_course_modules(course=course, module_ids_in_order=[second.id, first.id])

        first.refresh_from_db()
        second.refresh_from_db()

        self.assertEqual(first.order, 2)
        self.assertEqual(second.order, 1)

    def test_create_and_move_lesson(self):
        course = create_course_factory()
        source = create_course_module_factory(course=course, order=1)
        target = create_course_module_factory(course=course, order=2)
        lesson = create_course_lesson(
            course=course,
            module=source,
            title="Тема",
        )

        moved = move_course_lesson(
            lesson=lesson,
            target_module=target,
        )

        self.assertEqual(moved.module, target)

    def test_reorder_course_lessons(self):
        course = create_course_factory()
        module = create_course_module_factory(course=course)
        first = create_course_lesson_factory(course=course, module=module, order=1, title="1")
        second = create_course_lesson_factory(course=course, module=module, order=2, title="2")

        reorder_course_lessons(module=module, lesson_ids_in_order=[second.id, first.id])

        first.refresh_from_db()
        second.refresh_from_db()

        self.assertEqual(first.order, 2)
        self.assertEqual(second.order, 1)

    def test_create_course_material(self):
        lesson = create_course_lesson_factory()

        material = create_course_material(
            course=lesson.course,
            lesson=lesson,
            title="Методичка",
            file=create_course_file(),
        )

        self.assertEqual(material.lesson, lesson)
        self.assertEqual(material.course, lesson.course)


class CourseAssignmentServicesTestCase(TestCase):
    def test_assign_course_to_group(self):
        context = create_course_with_context()
        course = context["course"]
        group = context["group"]

        assignment = assign_course_to_group(
            course=course,
            group=group,
            assigned_by=course.author,
        )

        self.assertEqual(assignment.course, course)
        self.assertEqual(assignment.group, group)

    def test_assign_course_to_student(self):
        course = create_course_factory()
        student = create_course_student()

        assignment = assign_course_to_student(
            course=course,
            student=student,
            assigned_by=course.author,
        )

        self.assertEqual(assignment.student, student)

    def test_create_and_cancel_enrollment(self):
        course = create_course_factory()
        student = create_course_student()
        enrollment = create_course_enrollment(
            course=course,
            student=student,
        )

        cancelled = cancel_course_enrollment(enrollment=enrollment)
        self.assertEqual(cancelled.status, CourseEnrollment.StatusChoices.CANCELLED)

    def test_remove_assignment_with_enrollments_only_deactivates(self):
        course = create_course_factory()
        student = create_course_student()

        assignment = assign_course_to_student(
            course=course,
            student=student,
            assigned_by=course.author,
        )
        create_course_enrollment(
            course=course,
            student=student,
            assignment=assignment,
        )

        remove_course_assignment(assignment=assignment)
        assignment.refresh_from_db()

        self.assertFalse(assignment.is_active)


class CourseProgressServicesTestCase(TestCase):
    def test_start_course_enrollment(self):
        enrollment = create_course_enrollment_factory()

        updated = start_course_enrollment(enrollment=enrollment)

        self.assertEqual(updated.status, CourseEnrollment.StatusChoices.IN_PROGRESS)
        self.assertIsNotNone(updated.started_at)

    def test_mark_lesson_in_progress(self):
        lesson = create_course_lesson_factory()
        enrollment = create_course_enrollment_factory(course=lesson.course)

        lesson_progress = mark_lesson_in_progress(
            enrollment=enrollment,
            lesson=lesson,
        )

        self.assertEqual(lesson_progress.status, LessonProgress.StatusChoices.IN_PROGRESS)

    def test_mark_lesson_completed_and_recalculate_progress(self):
        lesson = create_course_lesson_factory()
        enrollment = create_course_enrollment_factory(course=lesson.course)

        lesson_progress = mark_lesson_completed(
            enrollment=enrollment,
            lesson=lesson,
            spent_minutes=15,
            attempts_increment=True,
        )

        self.assertEqual(lesson_progress.status, LessonProgress.StatusChoices.COMPLETED)

        progress = recalculate_course_progress(enrollment=enrollment)
        self.assertEqual(progress.progress_percent, 100)

        enrollment.refresh_from_db()
        self.assertEqual(enrollment.status, CourseEnrollment.StatusChoices.COMPLETED)
