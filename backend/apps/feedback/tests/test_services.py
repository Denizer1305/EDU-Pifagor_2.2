from __future__ import annotations

import tempfile
from pathlib import Path

from django.test import TestCase, override_settings

from apps.feedback.models import FeedbackRequest
from apps.feedback.services import (
    archive_feedback_request,
    create_contact_feedback_request,
    create_error_feedback_request,
    mark_feedback_as_spam,
    mark_feedback_in_progress,
    reject_feedback_request,
    resolve_feedback_request,
)
from apps.feedback.tests.factories import (
    create_feedback_admin_user,
    create_feedback_request,
    create_feedback_user,
    create_uploaded_file,
)


TEST_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class FeedbackServicesTestCase(TestCase):
    def test_create_contact_feedback_request(self):
        file = create_uploaded_file(name="contact.pdf")

        feedback_request = create_contact_feedback_request(
            subject="Вопрос по расписанию",
            message="Подскажите, где посмотреть расписание?",
            full_name="Иван Иванов",
            email="ivan@example.com",
            phone="+79990000000",
            is_personal_data_consent=True,
            files=[file],
        )

        self.assertEqual(feedback_request.source, FeedbackRequest.SourceChoices.CONTACTS_PAGE)
        self.assertEqual(feedback_request.attachments.count(), 1)
        self.assertEqual(feedback_request.email, "ivan@example.com")

    def test_create_error_feedback_request_autofills_authenticated_user_data(self):
        user = create_feedback_user(email="auth_user@example.com")

        feedback_request = create_error_feedback_request(
            user=user,
            subject="",
            message="При открытии урока появилась ошибка.",
            is_personal_data_consent=True,
            error_title="Ошибка загрузки урока",
            error_code="LESSON_LOAD_FAILED",
            error_details="TypeError: Cannot read properties of undefined",
        )

        self.assertEqual(feedback_request.source, FeedbackRequest.SourceChoices.ERROR_MODAL)
        self.assertEqual(feedback_request.type, FeedbackRequest.TypeChoices.BUG)
        self.assertEqual(feedback_request.subject, "Ошибка загрузки урока")
        self.assertEqual(feedback_request.user, user)
        self.assertEqual(feedback_request.email, user.email)

    def test_mark_feedback_in_progress(self):
        admin_user = create_feedback_admin_user()
        feedback_request = create_feedback_request(
            status=FeedbackRequest.StatusChoices.NEW,
            email="progress_service@example.com",
        )

        updated = mark_feedback_in_progress(
            feedback_request=feedback_request,
            admin_user=admin_user,
            internal_note="Взято в работу",
        )

        self.assertEqual(updated.status, FeedbackRequest.StatusChoices.IN_PROGRESS)
        self.assertEqual(updated.internal_note, "Взято в работу")

    def test_resolve_feedback_request(self):
        admin_user = create_feedback_admin_user()
        feedback_request = create_feedback_request(
            status=FeedbackRequest.StatusChoices.IN_PROGRESS,
            email="resolve_service@example.com",
        )

        updated = resolve_feedback_request(
            feedback_request=feedback_request,
            admin_user=admin_user,
            reply_message="Проблема решена",
            internal_note="Исправлено на backend",
        )

        self.assertEqual(updated.status, FeedbackRequest.StatusChoices.RESOLVED)
        self.assertTrue(updated.is_processed)
        self.assertEqual(updated.processed_by, admin_user)
        self.assertEqual(updated.reply_message, "Проблема решена")

    def test_reject_feedback_request(self):
        admin_user = create_feedback_admin_user()
        feedback_request = create_feedback_request(
            email="reject_service@example.com",
        )

        updated = reject_feedback_request(
            feedback_request=feedback_request,
            admin_user=admin_user,
            reply_message="Запрос отклонён",
        )

        self.assertEqual(updated.status, FeedbackRequest.StatusChoices.REJECTED)
        self.assertTrue(updated.is_processed)
        self.assertEqual(updated.processed_by, admin_user)

    def test_mark_feedback_as_spam(self):
        admin_user = create_feedback_admin_user()
        feedback_request = create_feedback_request(
            email="spam_service@example.com",
        )

        updated = mark_feedback_as_spam(
            feedback_request=feedback_request,
            admin_user=admin_user,
            internal_note="Подозрительное обращение",
        )

        self.assertEqual(updated.status, FeedbackRequest.StatusChoices.SPAM)
        self.assertTrue(updated.is_spam_suspected)
        self.assertTrue(updated.is_processed)

    def test_archive_feedback_request(self):
        admin_user = create_feedback_admin_user()
        feedback_request = create_feedback_request(
            status=FeedbackRequest.StatusChoices.RESOLVED,
            is_processed=True,
            email="archive_service@example.com",
        )

        updated = archive_feedback_request(
            feedback_request=feedback_request,
            admin_user=admin_user,
            internal_note="Переведено в архив",
        )

        self.assertEqual(updated.status, FeedbackRequest.StatusChoices.ARCHIVED)
        self.assertEqual(updated.internal_note, "Переведено в архив")
