from __future__ import annotations

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.course.models import (
    Course,
    CourseAssignment,
    CourseEnrollment,
    CourseLesson,
    CourseMaterial,
    CourseProgress,
)
from apps.course.tests.factories import (
    create_course,
    create_course_enrollment,
    create_course_lesson,
    create_course_material,
    create_course_module,
    create_course_progress,
    create_course_student,
    create_course_with_context,
)


class CourseModelTestCase(TestCase):
    def test_course_generates_code_and_slug(self):
        course = create_course(title="Подготовка к ЕГЭ по математике")

        self.assertTrue(course.code)
        self.assertTrue(course.slug)
        self.assertNotEqual(course.slug, "")

    def test_course_sets_published_at_on_save(self):
        course = create_course(
            status=Course.StatusChoices.PUBLISHED,
            title="Опубликованный курс",
        )

        self.assertIsNotNone(course.published_at)

    def test_course_sets_archived_at_on_save(self):
        course = create_course(
            status=Course.StatusChoices.ARCHIVED,
            is_active=False,
            title="Архивный курс",
        )

        self.assertIsNotNone(course.archived_at)

    def test_course_rejects_invalid_dates(self):
        course = create_course()
        course.starts_at = course.created_at
        course.ends_at = course.created_at.replace(year=course.created_at.year - 1)

        with self.assertRaises(ValidationError):
            course.full_clean()

    def test_course_rejects_group_subject_with_other_subject(self):
        context = create_course_with_context()
        another_subject = create_course_with_context()["subject"]
        course = context["course"]
        course.subject = another_subject

        with self.assertRaises(ValidationError):
            course.full_clean()


class CourseModuleLessonMaterialModelTestCase(TestCase):
    def test_module_requires_positive_order(self):
        module = create_course_module()
        module.order = 0

        with self.assertRaises(ValidationError):
            module.full_clean()

    def test_video_lesson_requires_video_url(self):
        lesson = create_course_lesson()
        lesson.lesson_type = CourseLesson.LessonTypeChoices.VIDEO
        lesson.video_url = ""

        with self.assertRaises(ValidationError):
            lesson.full_clean()

    def test_link_material_requires_external_url(self):
        material = create_course_material()
        material.material_type = CourseMaterial.MaterialTypeChoices.LINK
        material.file = None
        material.external_url = ""

        with self.assertRaises(ValidationError):
            material.full_clean()

    def test_material_attached_to_lesson_inherits_course(self):
        lesson = create_course_lesson()
        material = create_course_material(
            course=None,
            lesson=lesson,
        )

        self.assertEqual(material.course_id, lesson.course_id)


class CourseAssignmentEnrollmentModelTestCase(TestCase):
    def test_group_assignment_requires_group(self):
        assignment = CourseAssignment(
            course=create_course(),
            assignment_type=CourseAssignment.AssignmentTypeChoices.GROUP,
        )

        with self.assertRaises(ValidationError):
            assignment.full_clean()

    def test_student_assignment_requires_student(self):
        assignment = CourseAssignment(
            course=create_course(),
            assignment_type=CourseAssignment.AssignmentTypeChoices.STUDENT,
        )

        with self.assertRaises(ValidationError):
            assignment.full_clean()

    def test_completed_enrollment_sets_progress_to_100(self):
        enrollment = create_course_enrollment(
            status=CourseEnrollment.StatusChoices.COMPLETED,
            progress_percent=20,
        )

        self.assertEqual(enrollment.progress_percent, 100)
        self.assertIsNotNone(enrollment.completed_at)

    def test_enrollment_rejects_assignment_from_other_course(self):
        first_course = create_course()
        second_course = create_course()
        assignment = CourseAssignment.objects.create(
            course=second_course,
            assignment_type=CourseAssignment.AssignmentTypeChoices.STUDENT,
            student=create_course_student(),
            auto_enroll=True,
            is_active=True,
        )
        enrollment = CourseEnrollment(
            course=first_course,
            student=create_course_student(),
            assignment=assignment,
            status=CourseEnrollment.StatusChoices.ENROLLED,
            progress_percent=0,
        )

        with self.assertRaises(ValidationError):
            enrollment.full_clean()


class CourseProgressModelTestCase(TestCase):
    def test_course_progress_rejects_invalid_counts(self):
        progress = create_course_progress(
            total_lessons_count=2,
            completed_lessons_count=2,
        )
        progress.completed_lessons_count = 3

        with self.assertRaises(ValidationError):
            progress.full_clean()

    def test_course_progress_completion_sets_completed_at(self):
        progress = create_course_progress(
            total_lessons_count=4,
            completed_lessons_count=4,
            required_lessons_count=4,
            completed_required_lessons_count=4,
            progress_percent=100,
        )

        self.assertIsNotNone(progress.completed_at)
