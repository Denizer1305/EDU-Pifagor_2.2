from __future__ import annotations

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.course.models import Course, CourseTeacher
from apps.course.services import (
    add_teacher_to_course,
    archive_course,
    create_course,
    duplicate_course,
    publish_course,
    remove_teacher_from_course,
    update_course,
)
from apps.course.tests.factories import (
    create_course as create_course_factory,
)
from apps.course.tests.factories import (
    create_course_author,
)
from apps.course.tests.factories import (
    create_course_lesson as create_course_lesson_factory,
)
from apps.course.tests.factories import (
    create_course_material as create_course_material_factory,
)
from apps.course.tests.factories import (
    create_course_module as create_course_module_factory,
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
        lesson = create_course_lesson_factory(
            course=course,
            module=module,
            title="Урок 1",
        )
        create_course_material_factory(
            course=course,
            lesson=lesson,
            title="Файл 1",
        )

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
