from importlib import import_module

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CoursesConfig(AppConfig):
    """Конфигурация приложения users."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.course"
    label = "course"
    verbose_name = _("Курсы")

    def ready(self) -> None:
        """Инициализирует обработчики приложения при запуске."""
        try:
            import_module("apps.course.signals")
        except ModuleNotFoundError:
            pass
