from contextlib import suppress
from importlib import import_module

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class EducationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.education"
    label = "education"
    verbose_name = _("Образование")

    def ready(self) -> None:
        """Инициализирует обработчики приложения при запуске."""
        with suppress(ModuleNotFoundError):
            import_module("apps.education.signals")
