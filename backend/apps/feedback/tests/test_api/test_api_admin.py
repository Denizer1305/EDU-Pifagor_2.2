from __future__ import annotations

from django.urls import reverse
from rest_framework import status

from apps.feedback.models import FeedbackRequest
from apps.feedback.tests.test_api.api_base import FeedbackApiBaseTestCase
from apps.feedback.tests.factories import (
    create_feedback_attachment,
    create_feedback_request,
)


class FeedbackAdminApiTestCase(FeedbackApiBaseTestCase):
    """Тесты административного API обращений."""

    def test_admin_feedback_request_list(self):
        feedback_request = create_feedback_request(
            subject="Админский список",
            status=FeedbackRequest.StatusChoices.NEW,
        )

        self.client.force_authenticate(user=self.admin_user)

        url = reverse("feedback:admin-feedback-request-list")
        response = self.client.get(
            url,
            {
                "status": FeedbackRequest.StatusChoices.NEW,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_ids = [item["id"] for item in response.data]
        self.assertIn(feedback_request.id, returned_ids)

    def test_admin_feedback_request_list_filters_by_type_and_source(self):
        target = create_feedback_request(
            type=FeedbackRequest.TypeChoices.BUG,
            source=FeedbackRequest.SourceChoices.ERROR_MODAL,
            subject="Ошибка в модальном окне",
            error_code="BUG-001",
            error_title="Ошибка",
        )
        create_feedback_request(
            type=FeedbackRequest.TypeChoices.QUESTION,
            source=FeedbackRequest.SourceChoices.CONTACTS_PAGE,
            subject="Обычный вопрос",
        )

        self.client.force_authenticate(user=self.admin_user)

        url = reverse("feedback:admin-feedback-request-list")
        response = self.client.get(
            url,
            {
                "type": FeedbackRequest.TypeChoices.BUG,
                "source": FeedbackRequest.SourceChoices.ERROR_MODAL,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_ids = [item["id"] for item in response.data]
        self.assertIn(target.id, returned_ids)
        self.assertEqual(len(returned_ids), 1)

    def test_admin_feedback_request_list_filters_by_is_processed(self):
        processed_request = create_feedback_request(
            status=FeedbackRequest.StatusChoices.RESOLVED,
        )
        create_feedback_request(
            status=FeedbackRequest.StatusChoices.NEW,
        )

        self.client.force_authenticate(user=self.admin_user)

        url = reverse("feedback:admin-feedback-request-list")
        response = self.client.get(
            url,
            {
                "is_processed": "true",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_ids = [item["id"] for item in response.data]
        self.assertIn(processed_request.id, returned_ids)
        self.assertEqual(len(returned_ids), 1)

    def test_admin_feedback_request_list_filters_by_is_authenticated_sender(self):
        auth_request = create_feedback_request(
            user=self.user,
            subject="От авторизованного",
        )
        create_feedback_request(
            user=None,
            email="anonymous@example.com",
            subject="От анонимного",
        )

        self.client.force_authenticate(user=self.admin_user)

        url = reverse("feedback:admin-feedback-request-list")
        response = self.client.get(
            url,
            {
                "is_authenticated_sender": "true",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_ids = [item["id"] for item in response.data]
        self.assertIn(auth_request.id, returned_ids)
        self.assertEqual(len(returned_ids), 1)

    def test_admin_feedback_request_list_filters_by_has_attachments(self):
        with_files = create_feedback_request(
            subject="Со вложением",
        )
        create_feedback_attachment(feedback_request=with_files)

        create_feedback_request(
            subject="Без вложения",
        )

        self.client.force_authenticate(user=self.admin_user)

        url = reverse("feedback:admin-feedback-request-list")
        response = self.client.get(
            url,
            {
                "has_attachments": "true",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_ids = [item["id"] for item in response.data]
        self.assertIn(with_files.id, returned_ids)
        self.assertEqual(len(returned_ids), 1)

    def test_admin_feedback_request_list_filters_by_search(self):
        target = create_feedback_request(
            subject="Ошибка загрузки урока",
            error_code="LESSON_LOAD_FAILED",
            error_title="Ошибка загрузки урока",
        )
        create_feedback_request(
            subject="Просто вопрос",
        )

        self.client.force_authenticate(user=self.admin_user)

        url = reverse("feedback:admin-feedback-request-list")
        response = self.client.get(
            url,
            {
                "q": "LESSON_LOAD_FAILED",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_ids = [item["id"] for item in response.data]
        self.assertIn(target.id, returned_ids)
        self.assertEqual(len(returned_ids), 1)

    def test_admin_feedback_request_list_invalid_filter_returns_400(self):
        self.client.force_authenticate(user=self.admin_user)

        url = reverse("feedback:admin-feedback-request-list")
        response = self.client.get(
            url,
            {
                "created_at_from": "not-a-date",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_feedback_request_detail_patch_resolve(self):
        feedback_request = create_feedback_request(
            status=FeedbackRequest.StatusChoices.NEW,
        )

        self.client.force_authenticate(user=self.admin_user)

        url = reverse(
            "feedback:admin-feedback-request-detail",
            args=[feedback_request.id],
        )
        response = self.client.patch(
            url,
            data={
                "status": FeedbackRequest.StatusChoices.RESOLVED,
                "reply_message": "Исправлено",
                "internal_note": "Закрыто администратором",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["status"],
            FeedbackRequest.StatusChoices.RESOLVED,
        )
        self.assertTrue(response.data["is_processed"])
        self.assertEqual(
            response.data["processing"]["reply_message"],
            "Исправлено",
        )

    def test_regular_user_cannot_access_admin_feedback_list(self):
        self.client.force_authenticate(user=self.user)

        url = reverse("feedback:admin-feedback-request-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
