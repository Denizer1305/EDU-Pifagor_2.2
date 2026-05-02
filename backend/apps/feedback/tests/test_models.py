from __future__ import annotations

import tempfile

from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings

from apps.feedback.models import (
    FeedbackAttachment,
    FeedbackRequest,
    FeedbackRequestContact,
    FeedbackRequestProcessing,
    FeedbackRequestTechnical,
)
from apps.feedback.tests.factories import (
    create_feedback_request,
    create_feedback_user,
    create_uploaded_file,
)

TEST_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class FeedbackRequestModelTestCase(TestCase):
    def test_create_feedback_request(self):
        feedback_request = create_feedback_request(
            subject="Вопрос по платформе",
            message="Как получить доступ к материалам?",
            email="student@example.com",
        )

        self.assertEqual(feedback_request.subject, "Вопрос по платформе")
        self.assertEqual(feedback_request.status, FeedbackRequest.StatusChoices.NEW)
        self.assertEqual(feedback_request.contact.email, "student@example.com")

    def test_personal_data_consent_is_required(self):
        feedback_request = FeedbackRequest(
            source=FeedbackRequest.SourceChoices.CONTACTS_PAGE,
            type=FeedbackRequest.TypeChoices.QUESTION,
            subject="Без согласия",
            message="Сообщение без согласия на обработку данных",
            is_personal_data_consent=False,
        )

        with self.assertRaises(ValidationError):
            feedback_request.full_clean()

    def test_personal_data_consent_sets_timestamp_on_save(self):
        feedback_request = FeedbackRequest.objects.create(
            source=FeedbackRequest.SourceChoices.CONTACTS_PAGE,
            type=FeedbackRequest.TypeChoices.QUESTION,
            subject="Есть согласие",
            message="Сообщение с согласием",
            is_personal_data_consent=True,
        )

        self.assertIsNotNone(feedback_request.personal_data_consent_at)

    def test_feedback_request_str(self):
        feedback_request = create_feedback_request(
            subject="Тестовая тема",
        )

        self.assertIn("Тестовая тема", str(feedback_request))
        self.assertIn(feedback_request.get_status_display(), str(feedback_request))

    def test_contact_requires_email_for_anonymous_request(self):
        feedback_request = FeedbackRequest.objects.create(
            source=FeedbackRequest.SourceChoices.CONTACTS_PAGE,
            type=FeedbackRequest.TypeChoices.QUESTION,
            subject="Нет email",
            message="Сообщение без email",
            is_personal_data_consent=True,
        )

        contact = FeedbackRequestContact(
            feedback_request=feedback_request,
            full_name="Иван Иванов",
            email="",
            phone="+79990000000",
        )

        with self.assertRaises(ValidationError):
            contact.full_clean()

    def test_technical_context_required_for_error_modal(self):
        feedback_request = FeedbackRequest.objects.create(
            source=FeedbackRequest.SourceChoices.ERROR_MODAL,
            type=FeedbackRequest.TypeChoices.BUG,
            subject="Ошибка",
            message="Произошла ошибка в системе",
            is_personal_data_consent=True,
        )

        FeedbackRequestContact.objects.create(
            feedback_request=feedback_request,
            full_name="Иван Иванов",
            email="ivan@example.com",
        )

        technical = FeedbackRequestTechnical(
            feedback_request=feedback_request,
        )

        with self.assertRaises(ValidationError):
            technical.full_clean()

    def test_processing_requires_processed_at_for_final_status(self):
        feedback_request = FeedbackRequest.objects.create(
            source=FeedbackRequest.SourceChoices.CONTACTS_PAGE,
            type=FeedbackRequest.TypeChoices.QUESTION,
            status=FeedbackRequest.StatusChoices.RESOLVED,
            subject="Финальный статус",
            message="Сообщение",
            is_personal_data_consent=True,
        )

        FeedbackRequestContact.objects.create(
            feedback_request=feedback_request,
            email="user@example.com",
        )

        processing = FeedbackRequestProcessing(
            feedback_request=feedback_request,
            processed_by=create_feedback_user(email="processor@example.com"),
            processed_at=None,
        )

        with self.assertRaises(ValidationError):
            processing.full_clean()


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
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
        attachment.save()

        self.assertEqual(
            attachment.kind,
            FeedbackAttachment.FileKindChoices.PDF,
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
