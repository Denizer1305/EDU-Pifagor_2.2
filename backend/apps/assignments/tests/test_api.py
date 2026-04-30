from __future__ import annotations

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.assignments.models import (
    AssignmentAudience,
    AssignmentPublication,
    AssignmentSection,
    Submission
)
from apps.course.tests.factories import create_course
from apps.assignments.tests.factories import (
    create_assignment,
    create_assignment_audience,
    create_assignment_publication,
    create_assignment_question,
    create_course_enrollment,
    create_grade_record,
    create_assignment_policy,
    create_rubric,
    create_student_user,
    create_submission,
    create_submission_review,
    create_teacher_user,
)

COURSE_ENROLLMENT_AUDIENCE = getattr(
    AssignmentAudience.AudienceTypeChoices,
    "COURSE_ENROLLMENT",
    "course_enrollment",
)


class AssignmentApiTestCase(APITestCase):
    def setUp(self):
        self.teacher = create_teacher_user()
        self.student = create_student_user()

    def test_teacher_can_create_assignment(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.post(
            reverse("assignments:assignment-list-create"),
            {
                "title": "Контрольная по математике",
                "assignment_kind": "test",
                "control_scope": "current_control",
                "visibility": "assigned_only",
                "education_level": "school",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Контрольная по математике")

    def test_teacher_can_list_assignments(self):
        create_assignment(author=self.teacher, title="Моя работа")
        create_assignment(title="Чужая работа")

        self.client.force_authenticate(self.teacher)
        response = self.client.get(reverse("assignments:assignment-list-create"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Моя работа")

    def test_student_cannot_create_assignment(self):
        self.client.force_authenticate(self.student)

        response = self.client.post(
            reverse("assignments:assignment-list-create"),
            {
                "title": "Нельзя",
                "assignment_kind": "test",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_teacher_can_publish_assignment(self):
        assignment = create_assignment(author=self.teacher)
        create_assignment_question(assignment=assignment)

        self.client.force_authenticate(self.teacher)
        response = self.client.post(
            reverse("assignments:assignment-publish", kwargs={"pk": assignment.id}),
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], assignment.StatusChoices.PUBLISHED)

    def test_teacher_can_duplicate_assignment(self):
        assignment = create_assignment(author=self.teacher)
        create_assignment_question(assignment=assignment)

        self.client.force_authenticate(self.teacher)
        response = self.client.post(
            reverse("assignments:assignment-duplicate", kwargs={"pk": assignment.id}),
            {"title": "Копия"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Копия")


class AssignmentStructureApiTestCase(APITestCase):
    def setUp(self):
        self.teacher = create_teacher_user()
        self.assignment = create_assignment(author=self.teacher)

    def test_teacher_can_create_variant(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.post(
            reverse(
                "assignments:assignment-variant-list-create",
                kwargs={"assignment_id": self.assignment.id},
            ),
            {
                "title": "Вариант 1",
                "code": "VAR-1",
                "variant_number": 1,
                "order": 1,
                "is_default": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Вариант 1")

    def test_teacher_can_create_section(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.post(
            reverse(
                "assignments:assignment-section-list-create",
                kwargs={"assignment_id": self.assignment.id},
            ),
            {
                "title": "Часть А",
                "section_type": AssignmentSection.SectionTypeChoices.choices[0][0],
                "order": 1,
                "max_score": "10",
                "is_required": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Часть А")

    def test_teacher_can_create_question(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.post(
            reverse(
                "assignments:assignment-question-list-create",
                kwargs={"assignment_id": self.assignment.id},
            ),
            {
                "question_type": "single_choice",
                "prompt": "2+2=?",
                "answer_options_json": [{"id": "a", "text": "4"}],
                "correct_answer_json": {"id": "a"},
                "max_score": "1",
                "order": 1,
                "is_required": True,
                "requires_manual_review": False,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["prompt"], "2+2=?")

    def test_teacher_can_reorder_questions(self):
        q1 = create_assignment_question(assignment=self.assignment, order=1)
        q2 = create_assignment_question(assignment=self.assignment, order=2)

        self.client.force_authenticate(self.teacher)
        response = self.client.post(
            reverse(
                "assignments:assignment-question-reorder",
                kwargs={"assignment_id": self.assignment.id},
            ),
            {"question_ids": [q2.id, q1.id]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], q2.id)


class PublicationAndAudienceApiTestCase(APITestCase):
    def setUp(self):
        self.teacher = create_teacher_user()
        self.student = create_student_user()
        self.course = create_course(author=self.teacher)
        self.course_enrollment = create_course_enrollment(
            student=self.student,
            course=self.course,
        )
        self.assignment = create_assignment(author=self.teacher, course=self.course)
        self.publication = create_assignment_publication(
            assignment=self.assignment,
            course=self.course,
            published_by=self.teacher,
        )

    def test_teacher_can_create_publication(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.post(
            reverse("assignments:assignment-publication-list-create"),
            {
                "assignment_id": self.assignment.id,
                "course_id": self.course_enrollment.course.id,
                "title_override": "Итоговая публикация",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title_override"], "Итоговая публикация")

    def test_teacher_can_publish_publication(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.post(
            reverse(
                "assignments:assignment-publication-publish",
                kwargs={"pk": self.publication.id},
            ),
            {},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], AssignmentPublication.StatusChoices.PUBLISHED)

    def test_teacher_can_assign_student_audience(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.post(
            reverse(
                "assignments:assignment-audience-list-create",
                kwargs={"publication_id": self.publication.id},
            ),
            {
                "audience_type": "student",
                "student_id": self.student.id,
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["student"]["id"], self.student.id)

    def test_teacher_can_assign_course_enrollment(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.post(
            reverse(
                "assignments:assignment-audience-list-create",
                kwargs={"publication_id": self.publication.id},
            ),
            {
                "audience_type": COURSE_ENROLLMENT_AUDIENCE,
                "course_enrollment_id": self.course_enrollment.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class SubmissionApiTestCase(APITestCase):
    def setUp(self):
        self.teacher = create_teacher_user()
        self.student = create_student_user()
        self.course_enrollment = create_course_enrollment(student=self.student)
        self.assignment = create_assignment(author=self.teacher, course=self.course_enrollment.course)
        create_assignment_policy(self.assignment, attempts_limit=2)
        self.question = create_assignment_question(assignment=self.assignment)
        self.publication = create_assignment_publication(
            assignment=self.assignment,
            course=self.course_enrollment.course,
            published_by=self.teacher,
            status=AssignmentPublication.StatusChoices.PUBLISHED,
        )
        create_assignment_audience(
            publication=self.publication,
            audience_type=COURSE_ENROLLMENT_AUDIENCE,
            course_enrollment=self.course_enrollment,
        )

    def test_student_can_start_submission(self):
        self.client.force_authenticate(self.student)

        response = self.client.post(
            reverse("assignments:submission-start"),
            {
                "publication_id": self.publication.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["student"]["id"], self.student.id)

    def test_student_can_save_answer(self):
        submission = create_submission(
            publication=self.publication,
            assignment=self.assignment,
            student=self.student,
        )

        self.client.force_authenticate(self.student)
        response = self.client.post(
            reverse(
                "assignments:submission-answer-save",
                kwargs={"submission_id": submission.id},
            ),
            {
                "question_id": self.question.id,
                "answer_text": "Мой ответ",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], submission.id)

    def test_student_can_submit_submission(self):
        submission = create_submission(
            publication=self.publication,
            assignment=self.assignment,
            student=self.student,
        )

        self.client.force_authenticate(self.student)
        response = self.client.post(
            reverse(
                "assignments:submission-submit",
                kwargs={"submission_id": submission.id},
            ),
            {"confirm": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], Submission.StatusChoices.SUBMITTED)

    def test_student_can_retry_submission(self):
        submission = create_submission(
            publication=self.publication,
            assignment=self.assignment,
            student=self.student,
            status=Submission.StatusChoices.SUBMITTED,
        )

        self.client.force_authenticate(self.student)
        response = self.client.post(
            reverse(
                "assignments:submission-retry",
                kwargs={"submission_id": submission.id},
            ),
            {"confirm": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(response.data["id"], submission.id)


class ReviewApiTestCase(APITestCase):
    def setUp(self):
        self.teacher = create_teacher_user()
        self.student = create_student_user()
        self.assignment = create_assignment(author=self.teacher)
        self.question = create_assignment_question(
            assignment=self.assignment,
            requires_manual_review=True,
        )
        self.publication = create_assignment_publication(
            assignment=self.assignment,
            published_by=self.teacher,
        )
        self.submission = create_submission(
            publication=self.publication,
            assignment=self.assignment,
            student=self.student,
            status=Submission.StatusChoices.SUBMITTED,
        )

    def test_teacher_can_start_review(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.post(
            reverse(
                "assignments:submission-review-start",
                kwargs={"submission_id": self.submission.id},
            ),
            {"confirm": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["submission_id"], self.submission.id)

    def test_teacher_can_view_reviews(self):
        review = create_submission_review(submission=self.submission, reviewer=self.teacher)

        self.client.force_authenticate(self.teacher)
        response = self.client.get(
            reverse("assignments:submission-review-detail", kwargs={"pk": review.id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], review.id)

    def test_teacher_can_create_review_comment(self):
        review = create_submission_review(submission=self.submission, reviewer=self.teacher)

        self.client.force_authenticate(self.teacher)
        response = self.client.post(
            reverse(
                "assignments:review-comment-create",
                kwargs={"review_id": review.id},
            ),
            {
                "comment_type": "general",
                "message": "Нужно подробнее объяснить решение",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "Нужно подробнее объяснить решение")


class RubricAndGradeApiTestCase(APITestCase):
    def setUp(self):
        self.teacher = create_teacher_user()
        self.student = create_student_user()
        self.assignment = create_assignment(author=self.teacher)
        self.publication = create_assignment_publication(
            assignment=self.assignment,
            published_by=self.teacher,
        )
        self.submission = create_submission(
            publication=self.publication,
            assignment=self.assignment,
            student=self.student,
            status=Submission.StatusChoices.SUBMITTED,
        )

    def test_teacher_can_create_rubric(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.post(
            reverse("assignments:rubric-list-create"),
            {
                "title": "Рубрика проверки",
                "description": "Критерии",
                "assignment_kind": "essay",
                "is_template": True,
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Рубрика проверки")

    def test_teacher_can_create_grade_from_submission(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.post(
            reverse(
                "assignments:grade-create-from-submission",
                kwargs={"submission_id": self.submission.id},
            ),
            {"is_final": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["submission_id"], self.submission.id)

    def test_student_can_view_own_grade(self):
        grade = create_grade_record(submission=self.submission, graded_by=self.teacher)

        self.client.force_authenticate(self.student)
        response = self.client.get(
            reverse("assignments:grade-detail", kwargs={"pk": grade.id})
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["student"]["id"], self.student.id)


class AnalyticsApiTestCase(APITestCase):
    def setUp(self):
        self.teacher = create_teacher_user()
        self.student = create_student_user()
        self.course = create_course(author=self.teacher)
        self.course_enrollment = create_course_enrollment(
            student=self.student,
            course=self.course,
        )
        self.assignment = create_assignment(author=self.teacher, course=self.course)
        self.publication = create_assignment_publication(
            assignment=self.assignment,
            course=self.course,
            published_by=self.teacher,
            status=AssignmentPublication.StatusChoices.PUBLISHED,
        )
        self.submission = create_submission(
            publication=self.publication,
            assignment=self.assignment,
            student=self.student,
            status=Submission.StatusChoices.SUBMITTED,
            final_score=8,
            percentage=80,
            passed=True,
        )

    def test_teacher_can_get_assignment_statistics(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.get(
            reverse(
                "assignments:assignment-statistics",
                kwargs={"assignment_id": self.assignment.id},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["assignment_id"], self.assignment.id)

    def test_teacher_can_get_publication_statistics(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.get(
            reverse(
                "assignments:publication-statistics",
                kwargs={"publication_id": self.publication.id},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["publication_id"], self.publication.id)

    def test_teacher_can_get_student_progress(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.get(
            reverse(
                "assignments:student-assignment-progress",
                kwargs={
                    "assignment_id": self.assignment.id,
                    "student_id": self.student.id,
                },
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["student_id"], self.student.id)

    def test_teacher_can_get_course_dashboard(self):
        self.client.force_authenticate(self.teacher)

        response = self.client.get(
            reverse(
                "assignments:course-assignment-dashboard",
                kwargs={"course_id": self.course_enrollment.course.id},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["course_id"], self.course_enrollment.course.id)
