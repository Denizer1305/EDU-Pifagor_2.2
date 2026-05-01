from __future__ import annotations

from apps.users.constants import ROLE_STUDENT
from apps.users.services.role_services import (
    assign_role_to_user,
    list_user_role_codes,
    remove_role_from_user,
    user_has_role,
)
from apps.users.tests.test_services.service_base import BaseUsersServiceTestCase


class RoleServicesTestCase(BaseUsersServiceTestCase):
    def test_assign_and_remove_role(self):
        user = self.create_user("role-user@example.com")

        assign_role_to_user(user, ROLE_STUDENT)
        self.assertTrue(user_has_role(user, ROLE_STUDENT))

        remove_role_from_user(user, ROLE_STUDENT)
        self.assertFalse(user_has_role(user, ROLE_STUDENT))

    def test_list_user_role_codes(self):
        user = self.create_user("role-list@example.com")

        assign_role_to_user(user, ROLE_STUDENT)

        self.assertIn(
            ROLE_STUDENT,
            list_user_role_codes(user),
        )
