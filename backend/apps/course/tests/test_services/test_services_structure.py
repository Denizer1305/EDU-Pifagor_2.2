from __future__ import annotations

from django.test import TestCase

from apps.course.services import (
    create_course_lesson,
    create_course_material,
    create_course_module,
    move_course_lesson,
    reorder_course_lessons,
    reorder_course_modules,
)
from apps.course.tests.factories import (
    create_course as create_course_factory,
    create_course_file,
    create_course_lesson as create_course_lesson_factory,
    create_course_module as create_course_module_factory,
)


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
        first = create_course_module_factory(
            course=course,
            order=1,
            title="Первый",
        )
        second = create_course_module_factory(
            course=course,
            order=2,
            title="Второй",
        )

        reorder_course_modules(
            course=course,
            module_ids_in_order=[second.id, first.id],
        )

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
        first = create_course_lesson_factory(
            course=course,
            module=module,
            order=1,
            title="1",
        )
        second = create_course_lesson_factory(
            course=course,
            module=module,
            order=2,
            title="2",
        )

        reorder_course_lessons(
            module=module,
            lesson_ids_in_order=[second.id, first.id],
        )

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
