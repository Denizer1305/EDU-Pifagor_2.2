from __future__ import annotations

from apps.users.services.profile_services import update_base_profile
from apps.users.tests.test_services.service_base import BaseUsersServiceTestCase


class ProfileServicesTestCase(BaseUsersServiceTestCase):
    def test_update_base_profile(self):
        user = self.create_user("profile-update@example.com")

        profile = update_base_profile(
            user,
            first_name="Алексей",
            last_name="Обновленный",
            city="Москва",
        )

        self.assertEqual(profile.first_name, "Алексей")
        self.assertEqual(profile.city, "Москва")
