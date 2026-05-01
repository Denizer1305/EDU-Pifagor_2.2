from __future__ import annotations

from apps.users.constants import (
    ONBOARDING_STATUS_ACTIVE,
    ONBOARDING_STATUS_REJECTED,
)
from apps.users.services.user_services import (
    activate_user_onboarding,
    block_user,
    mark_user_email_verified,
    reject_user_onboarding,
)
from apps.users.tests.test_services.service_base import BaseUsersServiceTestCase


class UserServicesTestCase(BaseUsersServiceTestCase):
    def test_mark_user_email_verified(self):
        user = self.create_user("mark@example.com")

        mark_user_email_verified(user)
        user.refresh_from_db()

        self.assertTrue(user.is_email_verified)

    def test_activate_user_onboarding(self):
        user = self.create_user("activate@example.com")
        user.is_email_verified = True
        user.save(update_fields=["is_email_verified"])

        activate_user_onboarding(
            user,
            comment="Подтвержден",
        )
        user.refresh_from_db()

        self.assertEqual(
            user.onboarding_status,
            ONBOARDING_STATUS_ACTIVE,
        )

    def test_reject_user_onboarding(self):
        user = self.create_user("reject@example.com")

        reject_user_onboarding(
            user,
            comment="Недостаточно данных",
        )
        user.refresh_from_db()

        self.assertEqual(
            user.onboarding_status,
            ONBOARDING_STATUS_REJECTED,
        )

    def test_block_user(self):
        user = self.create_user("block@example.com")

        block_user(
            user,
            comment="Подозрительная активность",
        )
        user.refresh_from_db()

        self.assertFalse(user.is_active)
