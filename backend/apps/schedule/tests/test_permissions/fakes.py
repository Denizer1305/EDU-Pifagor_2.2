from __future__ import annotations

from types import SimpleNamespace


class FakeUserRoles:
    def __init__(self, *role_codes: str):
        self._user_roles = [
            SimpleNamespace(role=SimpleNamespace(code=role_code))
            for role_code in role_codes
        ]

    def select_related(self, *args, **kwargs):
        return self

    def all(self):
        return self._user_roles


def make_user(
    *,
    user_id: int = 1,
    role_codes: tuple[str, ...] = (),
    is_authenticated: bool = True,
    is_staff: bool = False,
    is_superuser: bool = False,
    student_group_id: int | None = None,
):
    user = SimpleNamespace(
        id=user_id,
        is_authenticated=is_authenticated,
        is_staff=is_staff,
        is_superuser=is_superuser,
        user_roles=FakeUserRoles(*role_codes),
    )

    if student_group_id is not None:
        user.student_profile = SimpleNamespace(group_id=student_group_id)

    return user


def make_request(method: str, user):
    return SimpleNamespace(method=method, user=user)
