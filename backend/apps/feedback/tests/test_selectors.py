from __future__ import annotations

from django.test import TestCase

from apps.feedback.models import FeedbackRequest
from apps.feedback.selectors import (
    get_feedback_request_by_id,
    get_feedback_requests_for_admin_queryset,
    get_my_feedback_requests_queryset,
    get_resolved_feedback_requests_queryset,
    get_spam_feedback_requests_queryset,
)
from apps.feedback.tests.factories import (
    create_feedback_request,
    create_feedback_user,
)


class FeedbackSelectorsTestCase(TestCase):
    def setUp(self):
        self.user = create_feedback_user(email="selector_user@example.com")
        self.other_user = create_feedback_user(email="selector_other@example.com")

    def test_get_my_feedback_requests_queryset_returns_only_own(self):
        own_request = create_feedback_request(
            user=self.user,
            subject="Моё обращение",
        )
        create_feedback_request(
            user=self.other_user,
            subject="Чужое обращение",
        )

        queryset = get_my_feedback_requests_queryset(user=self.user)

        self.assertIn(own_request, queryset)
        self.assertEqual(queryset.count(), 1)

    def test_get_feedback_requests_for_admin_queryset_filters_by_search(self):
        target = create_feedback_request(
            subject="Ошибка загрузки урока",
            error_code="LESSON_LOAD_FAILED",
            error_title="Ошибка загрузки",
        )
        create_feedback_request(
            subject="Обычный вопрос",
            error_code="QUESTION_CODE",
        )

        queryset = get_feedback_requests_for_admin_queryset(search="LESSON_LOAD_FAILED")

        self.assertIn(target, queryset)
        self.assertEqual(queryset.count(), 1)

    def test_get_feedback_requests_for_admin_queryset_filters_by_is_processed(self):
        processed_request = create_feedback_request(
            status=FeedbackRequest.StatusChoices.RESOLVED,
        )
        create_feedback_request(
            status=FeedbackRequest.StatusChoices.NEW,
        )

        queryset = get_feedback_requests_for_admin_queryset(is_processed=True)

        self.assertIn(processed_request, queryset)
        self.assertEqual(queryset.count(), 1)

    def test_get_feedback_request_by_id_returns_request_with_related_objects(self):
        feedback_request = create_feedback_request(
            user=self.user,
            subject="Детальный запрос",
            error_code="DETAIL-001",
        )

        result = get_feedback_request_by_id(feedback_request_id=feedback_request.id)

        self.assertIsNotNone(result)
        self.assertEqual(result.id, feedback_request.id)
        self.assertEqual(result.contact.email, self.user.email)
        self.assertEqual(result.technical.error_code, "DETAIL-001")

    def test_get_spam_feedback_requests_queryset(self):
        spam_request = create_feedback_request(
            status=FeedbackRequest.StatusChoices.SPAM,
            subject="Спам",
        )
        create_feedback_request(
            status=FeedbackRequest.StatusChoices.NEW,
            subject="Обычное обращение",
        )

        queryset = get_spam_feedback_requests_queryset()

        self.assertIn(spam_request, queryset)
        self.assertEqual(queryset.count(), 1)

    def test_get_resolved_feedback_requests_queryset(self):
        resolved_request = create_feedback_request(
            status=FeedbackRequest.StatusChoices.RESOLVED,
            subject="Решённое обращение",
        )
        create_feedback_request(
            status=FeedbackRequest.StatusChoices.NEW,
            subject="Новое обращение",
        )

        queryset = get_resolved_feedback_requests_queryset()

        self.assertIn(resolved_request, queryset)
        self.assertEqual(queryset.count(), 1)
