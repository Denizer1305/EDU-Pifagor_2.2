from __future__ import annotations

from django.test import TestCase

from apps.course.models import Course
from apps.course.selectors import (
    get_course_assignments_queryset,
    get_course_by_id,
    get_course_detail_queryset,
    get_course_enrollment_by_id,
    get_course_enrollments_queryset,
    get_course_lesson_by_id,
    get_course_material_queryset,
    get_course_module_by_id,
    get_course_progress_by_enrollment_id,
    get_course_progress_queryset,
    get_courses_queryset,
    get_course_structure_queryset,
    get_lesson_progress_queryset,
    get_public_courses_queryset,
    get_student_course_enrollments_queryset,
    get_teacher_courses_queryset,
)
from apps.course.tests.factories import (
    create_course,
    create_course_assignment,
    create_course_author,
    create_course_enrollment,
    create_course_lesson,
    create_course_material,
    create_course_module,
    create_course_progress,
    create_lesson_progress,
)


class CourseSelectorsTestCase(TestCase):
    def test_get_courses_queryset_filters_by_search(self):
        target = create_course(title="Подготовка к ЕГЭ")
        create_course(title="История России")

        queryset = get_courses_queryset(search="ЕГЭ")

        self.assertIn(target, queryset)
        self.assertEqual(queryset.count(), 1)

    def test_get_teacher_courses_queryset(self):
        teacher = create_course_author()
        course = create_course(author=teacher, title="Курс преподавателя")

        queryset = get_teacher_courses_queryset(teacher_id=teacher.id)

        self.assertIn(course, queryset)

    def test_get_public_courses_queryset(self):
        public_course = create_course(
            title="Публичный курс",
            status=Course.StatusChoices.PUBLISHED,
            visibility=Course.VisibilityChoices.PUBLIC_LINK,
        )
        create_course(
            title="Приватный курс",
            status=Course.StatusChoices.PUBLISHED,
            visibility=Course.VisibilityChoices.PRIVATE,
        )

        queryset = get_public_courses_queryset()

        self.assertIn(public_course, queryset)
        self.assertEqual(queryset.count(), 1)

    def test_get_course_by_id_returns_detail_queryset(self):
        course = create_course()
        result = get_course_by_id(course_id=course.id)

        self.assertIsNotNone(result)
        self.assertEqual(result.id, course.id)

    def test_get_course_detail_queryset(self):
        course = create_course()
        queryset = get_course_detail_queryset()

        self.assertIn(course, queryset)


class StructureSelectorsTestCase(TestCase):
    def test_get_course_structure_queryset(self):
        course = create_course()
        module = create_course_module(course=course)
        lesson = create_course_lesson(course=course, module=module)
        create_course_material(course=course, lesson=lesson)

        queryset = get_course_structure_queryset()
        self.assertIn(course, queryset)

    def test_get_course_module_by_id(self):
        module = create_course_module()
        result = get_course_module_by_id(module_id=module.id)

        self.assertIsNotNone(result)
        self.assertEqual(result.id, module.id)

    def test_get_course_lesson_by_id(self):
        lesson = create_course_lesson()
        result = get_course_lesson_by_id(lesson_id=lesson.id)

        self.assertIsNotNone(result)
        self.assertEqual(result.id, lesson.id)

    def test_get_course_material_queryset(self):
        material = create_course_material()
        queryset = get_course_material_queryset(course_id=material.course_id)

        self.assertIn(material, queryset)


class EnrollmentSelectorsTestCase(TestCase):
    def test_get_course_assignments_queryset(self):
        assignment = create_course_assignment()
        queryset = get_course_assignments_queryset(course_id=assignment.course_id)

        self.assertIn(assignment, queryset)

    def test_get_course_enrollments_queryset(self):
        enrollment = create_course_enrollment()
        queryset = get_course_enrollments_queryset(course_id=enrollment.course_id)

        self.assertIn(enrollment, queryset)

    def test_get_student_course_enrollments_queryset(self):
        enrollment = create_course_enrollment()
        queryset = get_student_course_enrollments_queryset(student_id=enrollment.student_id)

        self.assertIn(enrollment, queryset)

    def test_get_course_enrollment_by_id(self):
        enrollment = create_course_enrollment()
        result = get_course_enrollment_by_id(enrollment_id=enrollment.id)

        self.assertIsNotNone(result)
        self.assertEqual(result.id, enrollment.id)


class ProgressSelectorsTestCase(TestCase):
    def test_get_course_progress_queryset(self):
        progress = create_course_progress()
        queryset = get_course_progress_queryset(course_id=progress.enrollment.course_id)

        self.assertIn(progress, queryset)

    def test_get_course_progress_by_enrollment_id(self):
        progress = create_course_progress()
        result = get_course_progress_by_enrollment_id(enrollment_id=progress.enrollment_id)

        self.assertIsNotNone(result)
        self.assertEqual(result.id, progress.id)

    def test_get_lesson_progress_queryset(self):
        lesson_progress = create_lesson_progress()
        queryset = get_lesson_progress_queryset(enrollment_id=lesson_progress.enrollment_id)

        self.assertIn(lesson_progress, queryset)
