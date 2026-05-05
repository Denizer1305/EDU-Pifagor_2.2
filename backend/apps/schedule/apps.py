from contextlib import suppress
from importlib import import_module

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ScheduleConfig(AppConfig):
    """Конфигурация приложения users."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.schedule"
    label = "schedule"
    verbose_name = _("Расписание")

    def ready(self) -> None:
        """Инициализирует обработчики приложения при запуске."""
        with suppress(ModuleNotFoundError):
            import_module("apps.schedule.signals")
