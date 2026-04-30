from __future__ import annotations

from django.test import TestCase
from rest_framework.test import APIRequestFactory

from apps.assignments.permissions import (
    CanManageAssignmentObject,
    IsAdminOrSuperuser,
    IsAssignmentAuthorOrAdmin,
    IsStudentSubmissionOwner,
    IsSubmissionOwnerOrReviewerOrAdmin,
    IsTeacherOrAdmin,
    is_admin,
    is_student,
    is_teacher,
)
from apps.assignments.tests.factories import (
    create_admin_user,
    create_assignment,
    create_assignment_audience,
    create_assignment_publication,
    create_student_user,
    create_submission,
    create_teacher_user,
)


class DummyView:
    pass


class AssignmentPermissionsTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = DummyView()

        self.teacher = create_teacher_user()
        self.second_teacher = create_teacher_user()
        self.student = create_student_user()
        self.second_student = create_student_user()
        self.admin = create_admin_user()

        self.assignment = create_assignment(author=self.teacher)
        self.publication = create_assignment_publication(
            assignment=self.assignment,
            published_by=self.teacher,
        )
        self.audience = create_assignment_audience(
            publication=self.publication,
            student=self.student,
            audience_type="student",
        )
        self.submission = create_submission(
            publication=self.publication,
            assignment=self.assignment,
            student=self.student,
        )

    def _request(self, user):
        request = self.factory.get("/")
        request.user = user
        return request

    def test_role_helpers(self):
        self.assertTrue(is_teacher(self.teacher))
        self.assertFalse(is_teacher(self.student))

        self.assertTrue(is_student(self.student))
        self.assertFalse(is_student(self.teacher))

        self.assertTrue(is_admin(self.admin))
        self.assertFalse(is_admin(self.student))

    def test_is_teacher_or_admin_allows_teacher(self):
        permission = IsTeacherOrAdmin()
        request = self._request(self.teacher)

        self.assertTrue(permission.has_permission(request, self.view))

    def test_is_teacher_or_admin_allows_admin(self):
        permission = IsTeacherOrAdmin()
        request = self._request(self.admin)

        self.assertTrue(permission.has_permission(request, self.view))

    def test_is_teacher_or_admin_denies_student(self):
        permission = IsTeacherOrAdmin()
        request = self._request(self.student)

        self.assertFalse(permission.has_permission(request, self.view))

    def test_is_admin_or_superuser_allows_admin(self):
        permission = IsAdminOrSuperuser()
        request = self._request(self.admin)

        self.assertTrue(permission.has_permission(request, self.view))

    def test_is_admin_or_superuser_denies_teacher(self):
        permission = IsAdminOrSuperuser()
        request = self._request(self.teacher)

        self.assertFalse(permission.has_permission(request, self.view))

    def test_is_assignment_author_or_admin_allows_author(self):
        permission = IsAssignmentAuthorOrAdmin()
        request = self._request(self.teacher)

        self.assertTrue(
            permission.has_object_permission(request, self.view, self.assignment)
        )

    def test_is_assignment_author_or_admin_allows_admin(self):
        permission = IsAssignmentAuthorOrAdmin()
        request = self._request(self.admin)

        self.assertTrue(
            permission.has_object_permission(request, self.view, self.assignment)
        )

    def test_is_assignment_author_or_admin_denies_other_teacher(self):
        permission = IsAssignmentAuthorOrAdmin()
        request = self._request(self.second_teacher)

        self.assertFalse(
            permission.has_object_permission(request, self.view, self.assignment)
        )

    def test_can_manage_assignment_object_has_permission_for_teacher(self):
        permission = CanManageAssignmentObject()
        request = self._request(self.teacher)

        self.assertTrue(permission.has_permission(request, self.view))

    def test_can_manage_assignment_object_denies_student(self):
        permission = CanManageAssignmentObject()
        request = self._request(self.student)

        self.assertFalse(permission.has_permission(request, self.view))

    def test_can_manage_assignment_object_allows_author_for_assignment(self):
        permission = CanManageAssignmentObject()
        request = self._request(self.teacher)

        self.assertTrue(
            permission.has_object_permission(request, self.view, self.assignment)
        )

    def test_can_manage_assignment_object_allows_author_for_publication(self):
        permission = CanManageAssignmentObject()
        request = self._request(self.teacher)

        self.assertTrue(
            permission.has_object_permission(request, self.view, self.publication)
        )

    def test_can_manage_assignment_object_allows_author_for_audience(self):
        permission = CanManageAssignmentObject()
        request = self._request(self.teacher)

        self.assertTrue(
            permission.has_object_permission(request, self.view, self.audience)
        )

    def test_can_manage_assignment_object_denies_other_teacher(self):
        permission = CanManageAssignmentObject()
        request = self._request(self.second_teacher)

        self.assertFalse(
            permission.has_object_permission(request, self.view, self.assignment)
        )

    def test_can_manage_assignment_object_allows_admin(self):
        permission = CanManageAssignmentObject()
        request = self._request(self.admin)

        self.assertTrue(
            permission.has_object_permission(request, self.view, self.assignment)
        )

    def test_is_submission_owner_or_reviewer_or_admin_allows_owner(self):
        permission = IsSubmissionOwnerOrReviewerOrAdmin()
        request = self._request(self.student)

        self.assertTrue(
            permission.has_object_permission(request, self.view, self.submission)
        )

    def test_is_submission_owner_or_reviewer_or_admin_allows_assignment_author(self):
        permission = IsSubmissionOwnerOrReviewerOrAdmin()
        request = self._request(self.teacher)

        self.assertTrue(
            permission.has_object_permission(request, self.view, self.submission)
        )

    def test_is_submission_owner_or_reviewer_or_admin_allows_checked_by(self):
        self.submission.checked_by = self.second_teacher
        self.submission.save(update_fields=("checked_by", "updated_at"))

        permission = IsSubmissionOwnerOrReviewerOrAdmin()
        request = self._request(self.second_teacher)

        self.assertTrue(
            permission.has_object_permission(request, self.view, self.submission)
        )

    def test_is_submission_owner_or_reviewer_or_admin_allows_admin(self):
        permission = IsSubmissionOwnerOrReviewerOrAdmin()
        request = self._request(self.admin)

        self.assertTrue(
            permission.has_object_permission(request, self.view, self.submission)
        )

    def test_is_submission_owner_or_reviewer_or_admin_denies_other_student(self):
        permission = IsSubmissionOwnerOrReviewerOrAdmin()
        request = self._request(self.second_student)

        self.assertFalse(
            permission.has_object_permission(request, self.view, self.submission)
        )

    def test_is_student_submission_owner_allows_owner(self):
        permission = IsStudentSubmissionOwner()
        request = self._request(self.student)

        self.assertTrue(
            permission.has_object_permission(request, self.view, self.submission)
        )

    def test_is_student_submission_owner_denies_teacher(self):
        permission = IsStudentSubmissionOwner()
        request = self._request(self.teacher)

        self.assertFalse(
            permission.has_object_permission(request, self.view, self.submission)
        )

    def test_is_student_submission_owner_denies_other_student(self):
        permission = IsStudentSubmissionOwner()
        request = self._request(self.second_student)

        self.assertFalse(
            permission.has_object_permission(request, self.view, self.submission)
        )
