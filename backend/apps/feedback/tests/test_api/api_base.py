from __future__ import annotations

import tempfile

from django.test import override_settings
from rest_framework.test import APITestCase

from apps.feedback.tests.factories import (
    create_feedback_admin_user,
    create_feedback_user,
)


TEST_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class FeedbackApiBaseTestCase(APITestCase):
    """Базовый класс для API-тестов feedback."""

    def setUp(self):
        self.user = create_feedback_user(email="api_user@example.com")
        self.other_user = create_feedback_user(email="api_other@example.com")
        self.admin_user = create_feedback_admin_user()
