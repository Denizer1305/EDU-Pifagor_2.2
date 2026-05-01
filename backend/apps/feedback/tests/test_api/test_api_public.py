from __future__ import annotations

from django.urls import reverse
from rest_framework import status

from apps.feedback.models import FeedbackRequest
from apps.feedback.tests.test_api.api_base import FeedbackApiBaseTestCase
from apps.feedback.tests.factories import create_uploaded_file


class FeedbackPublicApiTestCase(FeedbackApiBaseTestCase):
    """Тесты публичного создания обращений."""

    def test_public_feedback_request_create(self):
        url = reverse("feedback:feedback-request-create")
        file = create_uploaded_file(name="contacts.pdf")

        response = self.client.post(
            url,
            data={
                "type": FeedbackRequest.TypeChoices.QUESTION,
                "subject": "Вопрос с сайта",
                "message": "Хочу узнать подробнее о платформе.",
                "full_name": "Иван Иванов",
                "email": "public@example.com",
                "phone": "+79990000000",
                "is_personal_data_consent": True,
                "attachments": [file],
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["subject"], "Вопрос с сайта")
        self.assertEqual(
            response.data["source"],
            FeedbackRequest.SourceChoices.CONTACTS_PAGE,
        )
        self.assertEqual(response.data["email"], "public@example.com")
        self.assertEqual(response.data["contact"]["email"], "public@example.com")
        self.assertEqual(len(response.data["attachments"]), 1)

    def test_error_feedback_create_for_authenticated_user(self):
        self.client.force_authenticate(user=self.user)

        url = reverse("feedback:feedback-error-create")
        file = create_uploaded_file(name="error.pdf")

        response = self.client.post(
            url,
            data={
                "type": FeedbackRequest.TypeChoices.BUG,
                "subject": "",
                "message": "При входе в урок возникла ошибка.",
                "is_personal_data_consent": True,
                "attachments": [file],
                "page_url": "https://edu-pifagor.ru/lesson/1",
                "frontend_route": "/lesson/1",
                "error_code": "LESSON_LOAD_FAILED",
                "error_title": "Ошибка загрузки урока",
                "error_details": "TypeError on frontend",
                "client_platform": "web",
                "app_version": "1.0.0",
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data["source"],
            FeedbackRequest.SourceChoices.ERROR_MODAL,
        )
        self.assertEqual(response.data["user"], self.user.id)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["contact"]["email"], self.user.email)
        self.assertEqual(
            response.data["technical"]["error_code"],
            "LESSON_LOAD_FAILED",
        )

    def test_error_feedback_create_requires_authentication(self):
        url = reverse("feedback:feedback-error-create")

        response = self.client.post(
            url,
            data={
                "message": "Произошла ошибка.",
                "is_personal_data_consent": True,
            },
            format="json",
        )

        self.assertIn(
            response.status_code,
            {
                status.HTTP_401_UNAUTHORIZED,
                status.HTTP_403_FORBIDDEN,
            },
        )
