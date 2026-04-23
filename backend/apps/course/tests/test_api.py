from __future__ import annotations

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.course.models import Course, CourseEnrollment, CourseTeacher
from apps.course.tests.factories import (
    create_course,
    create_course_assignment,
    create_course_author,
    create_course_enrollment,
    create_course_module,
    create_course_lesson,
    create_course_progress,
    create_course_student,
    create_course_with_context,
)


class CourseApiTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = create_course_author(email="course_teacher_api@example.com")
        self.student = create_course_student(email="course_student_api@example.com")
        self.other_teacher = create_course_author(email="course_other_teacher_api@example.com")

    def test_teacher_can_create_course(self):
        self.client.force_authenticate(user=self.teacher)
        url = reverse("course:course-list-create")

        response = self.client.post(
            url,
            data={
                "title": "Подготовка к ЕГЭ",
                "subtitle": "Профильный уровень",
                "description": "Авторский курс",
                "course_type": Course.CourseTypeChoices.EXAM_PREP,
                "visibility": Course.VisibilityChoices.ASSIGNED_ONLY,
                "level": Course.LevelChoices.EXAM,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Подготовка к ЕГЭ")
        self.assertEqual(
            response.data["course_type"],
            Course.CourseTypeChoices.EXAM_PREP,
        )

    def test_student_cannot_create_course(self):
        self.client.force_authenticate(user=self.student)
        url = reverse("course:course-list-create")

        response = self.client.post(
            url,
            data={"title": "Нельзя создать"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_can_get_course_list(self):
        course = create_course(author=self.teacher, title="Курс преподавателя")

        self.client.force_authenticate(user=self.teacher)
        url = reverse("course:course-list-create")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in response.data]
        self.assertIn(course.id, ids)

    def test_owner_can_publish_course(self):
        course = create_course(author=self.teacher)
        module = create_course_module(course=course)
        create_course_lesson(course=course, module=module)

        self.client.force_authenticate(user=self.teacher)
        url = reverse("course:course-publish", args=[course.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], Course.StatusChoices.PUBLISHED)

    def test_owner_cannot_publish_empty_course(self):
        course = create_course(author=self.teacher)

        self.client.force_authenticate(user=self.teacher)
        url = reverse("course:course-publish", args=[course.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_owner_can_add_teacher_to_course(self):
        course = create_course(author=self.teacher)

        self.client.force_authenticate(user=self.teacher)
        url = reverse("course:course-teacher-list-create", args=[course.id])
        response = self.client.post(
            url,
            data={
                "teacher": self.other_teacher.id,
                "role": CourseTeacher.RoleChoices.TEACHER,
                "can_manage_assignments": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            CourseTeacher.objects.filter(course=course, teacher=self.other_teacher).exists()
        )

    def test_teacher_can_create_module(self):
        course = create_course(author=self.teacher)

        self.client.force_authenticate(user=self.teacher)
        url = reverse("course:course-module-list-create", args=[course.id])
        response = self.client.post(
            url,
            data={"title": "Модуль 1"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Модуль 1")

    def test_teacher_can_create_lesson(self):
        course = create_course(author=self.teacher)
        module = create_course_module(course=course)

        self.client.force_authenticate(user=self.teacher)
        url = reverse("course:course-lesson-list-create", args=[module.id])
        response = self.client.post(
            url,
            data={
                "title": "Урок 1",
                "lesson_type": "text",
                "estimated_minutes": 20,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Урок 1")

    def test_teacher_can_move_lesson(self):
        course = create_course(author=self.teacher)
        first_module = create_course_module(course=course, title="Первый")
        second_module = create_course_module(course=course, title="Второй")
        lesson = create_course_lesson(course=course, module=first_module)

        self.client.force_authenticate(user=self.teacher)
        url = reverse("course:course-lesson-move", args=[lesson.id])
        response = self.client.post(
            url,
            data={"target_module": second_module.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        lesson.refresh_from_db()
        self.assertEqual(lesson.module_id, second_module.id)

    def test_public_list_returns_published_public_courses(self):
        public_course = create_course(
            title="Открытый курс",
            status=Course.StatusChoices.PUBLISHED,
            visibility=Course.VisibilityChoices.PUBLIC_LINK,
        )
        create_course(
            title="Закрытый курс",
            status=Course.StatusChoices.PUBLISHED,
            visibility=Course.VisibilityChoices.PRIVATE,
        )

        url = reverse("course:course-public-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in response.data]
        self.assertIn(public_course.id, ids)
        self.assertEqual(len(ids), 1)

    def test_public_detail_for_private_course_forbidden(self):
        course = create_course(
            status=Course.StatusChoices.PUBLISHED,
            visibility=Course.VisibilityChoices.PRIVATE,
        )

        url = reverse("course:course-public-detail", args=[course.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CourseAssignmentApiTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = create_course_author(email="assignment_teacher_api@example.com")
        self.student = create_course_student(email="assignment_student_api@example.com")
        self.context = create_course_with_context(author=self.teacher)
        self.course = self.context["course"]
        self.group = self.context["group"]

    def test_teacher_can_create_group_assignment(self):
        self.client.force_authenticate(user=self.teacher)
        url = reverse("course:course-assignment-list-create", args=[self.course.id])

        response = self.client.post(
            url,
            data={
                "assignment_type": "group",
                "group": self.group.id,
                "auto_enroll": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["assignment_type"], "group")

    def test_teacher_can_list_enrollments(self):
        enrollment = create_course_enrollment(course=self.course, student=self.student)

        self.client.force_authenticate(user=self.teacher)
        url = reverse("course:course-enrollment-list", args=[self.course.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in response.data]
        self.assertIn(enrollment.id, ids)

    def test_student_can_list_own_enrollments(self):
        enrollment = create_course_enrollment(course=self.course, student=self.student)

        self.client.force_authenticate(user=self.student)
        url = reverse("course:my-course-enrollment-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in response.data]
        self.assertIn(enrollment.id, ids)

    def test_student_can_cancel_own_enrollment(self):
        enrollment = create_course_enrollment(course=self.course, student=self.student)

        self.client.force_authenticate(user=self.student)
        url = reverse("course:course-enrollment-cancel", args=[enrollment.id])
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["status"],
            CourseEnrollment.StatusChoices.CANCELLED,
        )


class CourseProgressApiTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = create_course_author(email="progress_teacher_api@example.com")
        self.student = create_course_student(email="progress_student_api@example.com")
        self.course = create_course(author=self.teacher)
        self.module = create_course_module(course=self.course)
        self.lesson = create_course_lesson(course=self.course, module=self.module)
        self.enrollment = create_course_enrollment(course=self.course, student=self.student)
        self.progress = create_course_progress(enrollment=self.enrollment)

    def test_student_can_start_course(self):
        self.client.force_authenticate(user=self.student)
        url = reverse("course:course-enrollment-start", args=[self.enrollment.id])

        response = self.client.post(url, data={}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.status, CourseEnrollment.StatusChoices.IN_PROGRESS)

    def test_student_can_mark_lesson_in_progress(self):
        self.client.force_authenticate(user=self.student)
        url = reverse(
            "course:lesson-progress-in-progress",
            args=[self.enrollment.id, self.lesson.id],
        )

        response = self.client.post(url, data={}, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "in_progress")

    def test_student_can_complete_lesson(self):
        self.client.force_authenticate(user=self.student)
        url = reverse(
            "course:lesson-progress-complete",
            args=[self.enrollment.id, self.lesson.id],
        )

        response = self.client.post(
            url,
            data={
                "spent_minutes": 30,
                "attempts_increment": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "completed")

    def test_teacher_can_view_course_progress(self):
        self.client.force_authenticate(user=self.teacher)
        url = reverse("course:course-progress-detail", args=[self.enrollment.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["enrollment"], self.enrollment.id)
