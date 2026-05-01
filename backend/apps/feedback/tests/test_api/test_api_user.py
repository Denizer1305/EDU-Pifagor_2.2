from __future__ import annotations

from django.urls import reverse
from rest_framework import status

from apps.feedback.models import FeedbackRequest
from apps.feedback.tests.test_api.api_base import FeedbackApiBaseTestCase
from apps.feedback.tests.factories import (
    create_feedback_attachment,
    create_feedback_request,
)


class FeedbackUserApiTestCase(FeedbackApiBaseTestCase):
    """Тесты API личных обращений пользователя."""

    def test_my_feedback_request_list_returns_only_own(self):
        own_request = create_feedback_request(
            user=self.user,
            subject="Моё обращение",
        )
        create_feedback_request(
            user=self.other_user,
            subject="Чужое обращение",
        )

        self.client.force_authenticate(user=self.user)

        url = reverse("feedback:my-feedback-request-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_ids = [item["id"] for item in response.data]
        self.assertIn(own_request.id, returned_ids)
        self.assertEqual(len(returned_ids), 1)

    def test_my_feedback_request_list_filters_by_status(self):
        target = create_feedback_request(
            user=self.user,
            status=FeedbackRequest.StatusChoices.NEW,
            subject="Новый запрос",
        )
        create_feedback_request(
            user=self.user,
            status=FeedbackRequest.StatusChoices.RESOLVED,
            subject="Решённый запрос",
        )

        self.client.force_authenticate(user=self.user)

        url = reverse("feedback:my-feedback-request-list")
        response = self.client.get(
            url,
            {
                "status": FeedbackRequest.StatusChoices.NEW,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_ids = [item["id"] for item in response.data]
        self.assertIn(target.id, returned_ids)
        self.assertEqual(len(returned_ids), 1)

    def test_my_feedback_request_list_filters_by_search(self):
        target = create_feedback_request(
            user=self.user,
            subject="Ошибка открытия урока",
        )
        create_feedback_request(
            user=self.user,
            subject="Вопрос по расписанию",
        )

        self.client.force_authenticate(user=self.user)

        url = reverse("feedback:my-feedback-request-list")
        response = self.client.get(
            url,
            {
                "q": "открытия урока",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_ids = [item["id"] for item in response.data]
        self.assertIn(target.id, returned_ids)
        self.assertEqual(len(returned_ids), 1)

    def test_my_feedback_request_list_filters_by_has_attachments(self):
        with_files = create_feedback_request(
            user=self.user,
            subject="С файлом",
        )
        create_feedback_attachment(feedback_request=with_files)

        create_feedback_request(
            user=self.user,
            subject="Без файла",
        )

        self.client.force_authenticate(user=self.user)

        url = reverse("feedback:my-feedback-request-list")
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

    def test_my_feedback_request_detail_for_owner(self):
        feedback_request = create_feedback_request(
            user=self.user,
            subject="Детальное обращение",
        )

        self.client.force_authenticate(user=self.user)

        url = reverse(
            "feedback:my-feedback-request-detail",
            args=[feedback_request.id],
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], feedback_request.id)
        self.assertEqual(response.data["contact"]["email"], self.user.email)

    def test_my_feedback_request_detail_denied_for_other_user(self):
        feedback_request = create_feedback_request(
            user=self.other_user,
        )

        self.client.force_authenticate(user=self.user)

        url = reverse(
            "feedback:my-feedback-request-detail",
            args=[feedback_request.id],
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
