from __future__ import annotations


def _normalize_registration_data(
    *,
    email: str,
    reset_email: str,
    first_name: str,
    last_name: str,
    patronymic: str,
    phone: str,
    position: str,
    employee_code: str,
    work_place: str,
    education_info: str,
) -> dict:
    """Нормализует строковые данные регистрации."""

    return {
        "email": (email or "").strip().lower(),
        "reset_email": (reset_email or "").strip().lower(),
        "first_name": (first_name or "").strip(),
        "last_name": (last_name or "").strip(),
        "patronymic": (patronymic or "").strip(),
        "phone": (phone or "").strip(),
        "position": (position or "").strip(),
        "employee_code": (employee_code or "").strip(),
        "work_place": (work_place or "").strip(),
        "education_info": (education_info or "").strip(),
    }
