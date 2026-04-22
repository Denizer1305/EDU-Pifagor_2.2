from __future__ import annotations

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.feedback.models import FeedbackAttachment, FeedbackRequest
from apps.feedback.tests.factories import (
    create_feedback_request,
    create_uploaded_file,
)


class FeedbackRequestModelTestCase(TestCase):
    def test_create_feedback_request(self):
        feedback_request = create_feedback_request(
            subject="Вопрос по платформе",
            message="Как получить доступ к материалам?",
            email="student@example.com",
        )

        self.assertEqual(feedback_request.subject, "Вопрос по платформе")
        self.assertEqual(feedback_request.status, FeedbackRequest.StatusChoices.NEW)

    def test_contacts_request_requires_email_for_anonymous_sender(self):
        feedback_request = FeedbackRequest(
            source=FeedbackRequest.SourceChoices.CONTACTS_PAGE,
            type=FeedbackRequest.TypeChoices.QUESTION,
            subject="Нет email",
            message="Сообщение без email",
            email="",
            is_personal_data_consent=True,
        )

        with self.assertRaises(ValidationError):
            feedback_request.full_clean()

    def test_personal_data_consent_is_required(self):
        feedback_request = FeedbackRequest(
            source=FeedbackRequest.SourceChoices.CONTACTS_PAGE,
            type=FeedbackRequest.TypeChoices.QUESTION,
            subject="Без согласия",
            message="Сообщение без согласия на обработку данных",
            email="user@example.com",
            is_personal_data_consent=False,
        )

        with self.assertRaises(ValidationError):
            feedback_request.full_clean()

    def test_personal_data_consent_sets_timestamp(self):
        feedback_request = FeedbackRequest(
            source=FeedbackRequest.SourceChoices.CONTACTS_PAGE,
            type=FeedbackRequest.TypeChoices.QUESTION,
            subject="Есть согласие",
            message="Сообщение с согласием",
            email="user@example.com",
            is_personal_data_consent=True,
            personal_data_consent_at=None,
        )

        feedback_request.full_clean()

        self.assertIsNotNone(feedback_request.personal_data_consent_at)

    def test_spam_status_marks_spam_flag(self):
        feedback_request = FeedbackRequest(
            source=FeedbackRequest.SourceChoices.CONTACTS_PAGE,
            type=FeedbackRequest.TypeChoices.OTHER,
            status=FeedbackRequest.StatusChoices.SPAM,
            subject="Спам",
            message="Подозрительное сообщение",
            email="spam@example.com",
            is_personal_data_consent=True,
        )

        feedback_request.full_clean()

        self.assertTrue(feedback_request.is_spam_suspected)

    def test_error_details_length_validation(self):
        feedback_request = FeedbackRequest(
            source=FeedbackRequest.SourceChoices.ERROR_MODAL,
            type=FeedbackRequest.TypeChoices.BUG,
            subject="Ошибка",
            message="Произошла ошибка в системе",
            is_personal_data_consent=True,
            error_details="x" * 10001,
        )

        with self.assertRaises(ValidationError):
            feedback_request.full_clean()

    def test_feedback_request_str(self):
        feedback_request = create_feedback_request(
            subject="Тестовая тема",
            full_name="Иван Иванов",
            email="ivan@example.com",
        )

        self.assertIn("Тестовая тема", str(feedback_request))
        self.assertIn("Иван Иванов", str(feedback_request))


class FeedbackAttachmentModelTestCase(TestCase):
    def test_attachment_detects_pdf_type(self):
        feedback_request = create_feedback_request()
        file = create_uploaded_file(
            name="document.pdf",
            content_type="application/pdf",
        )

        attachment = FeedbackAttachment(
            feedback_request=feedback_request,
            file=file,
            original_name=file.name,
        )
        attachment.full_clean()

        self.assertEqual(
            attachment.file_type,
            FeedbackAttachment.FileTypeChoices.PDF,
        )

    def test_attachment_rejects_unsupported_extension(self):
        feedback_request = create_feedback_request()
        file = create_uploaded_file(
            name="archive.zip",
            content_type="application/zip",
        )

        attachment = FeedbackAttachment(
            feedback_request=feedback_request,
            file=file,
            original_name=file.name,
        )

        with self.assertRaises(ValidationError):
            attachment.full_clean()

    def test_attachment_rejects_large_file(self):
        feedback_request = create_feedback_request()
        file = create_uploaded_file(
            name="big.pdf",
            content=b"x" * (10 * 1024 * 1024 + 1),
            content_type="application/pdf",
        )

        attachment = FeedbackAttachment(
            feedback_request=feedback_request,
            file=file,
            original_name=file.name,
        )

        with self.assertRaises(ValidationError):
            attachment.full_clean()
