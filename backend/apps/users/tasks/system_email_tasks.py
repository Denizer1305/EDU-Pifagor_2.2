from __future__ import annotations

from celery import shared_task
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.users.tasks.email_common import (
    get_user_first_name,
    get_user_for_email_task,
    send_templated_email,
)


@shared_task(name="apps.users.tasks.send_birthday_email_task")
def send_birthday_email_task(user_id: int) -> None:
    """Отправляет поздравительное письмо с днём рождения."""

    user = get_user_for_email_task(user_id)
    if user is None:
        return

    context = {
        "email_title": _("С днем рождения!"),
        "heading": _("С днем рождения!"),
        "preheader": _("Команда Пифагора поздравляет вас."),
        "footer_note": _("Желаем вдохновения, роста и новых достижений."),
        "first_name": get_user_first_name(user),
        "current_year": timezone.now().year,
    }

    send_templated_email(
        subject=str(_("С днем рождения от платформы Пифагор")),
        to_email=user.email,
        html_template="templates/system/birthday.html",
        txt_template="templates/system/birthday.txt",
        context=context,
    )
