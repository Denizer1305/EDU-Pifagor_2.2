from __future__ import annotations

import tempfile

from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.feedback.models import FeedbackRequest
from apps.feedback.tests.factories import (
    create_feedback_admin_user,
    create_feedback_attachment,
    create_feedback_request,
    create_feedback_user,
    create_uploaded_file,
)


TEST_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class FeedbackApiTestCase(APITestCase):
    def setUp(self):
        self.user = create_feedback_user(email="api_user@example.com")
        self.other_user = create_feedback_user(email="api_other@example.com")
        self.admin_user = create_feedback_admin_user()

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
        response = self.client.get(url, {"status": FeedbackRequest.StatusChoices.NEW})

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
        response = self.client.get(url, {"q": "открытия урока"})

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
        response = self.client.get(url, {"has_attachments": "true"})

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
        url = reverse("feedback:my-feedback-request-detail", args=[feedback_request.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], feedback_request.id)
        self.assertEqual(response.data["contact"]["email"], self.user.email)

    def test_my_feedback_request_detail_denied_for_other_user(self):
        feedback_request = create_feedback_request(
            user=self.other_user,
        )

        self.client.force_authenticate(user=self.user)
        url = reverse("feedback:my-feedback-request-detail", args=[feedback_request.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_feedback_request_list(self):
        feedback_request = create_feedback_request(
            subject="Админский список",
            status=FeedbackRequest.StatusChoices.NEW,
        )

        self.client.force_authenticate(user=self.admin_user)
        url = reverse("feedback:admin-feedback-request-list")
        response = self.client.get(url, {"status": FeedbackRequest.StatusChoices.NEW})

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
        response = self.client.get(url, {"is_processed": "true"})

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
        response = self.client.get(url, {"is_authenticated_sender": "true"})

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
        response = self.client.get(url, {"has_attachments": "true"})

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
        response = self.client.get(url, {"q": "LESSON_LOAD_FAILED"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_ids = [item["id"] for item in response.data]
        self.assertIn(target.id, returned_ids)
        self.assertEqual(len(returned_ids), 1)

    def test_admin_feedback_request_list_invalid_filter_returns_400(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("feedback:admin-feedback-request-list")
        response = self.client.get(url, {"created_at_from": "not-a-date"})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_admin_feedback_request_detail_patch_resolve(self):
        feedback_request = create_feedback_request(
            status=FeedbackRequest.StatusChoices.NEW,
        )

        self.client.force_authenticate(user=self.admin_user)
        url = reverse("feedback:admin-feedback-request-detail", args=[feedback_request.id])
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
        self.assertEqual(response.data["processing"]["reply_message"], "Исправлено")

    def test_regular_user_cannot_access_admin_feedback_list(self):
        self.client.force_authenticate(user=self.user)
        url = reverse("feedback:admin-feedback-request-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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
            {status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN},
        )
