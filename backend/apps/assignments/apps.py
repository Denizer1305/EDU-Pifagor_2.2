from contextlib import suppress
from importlib import import_module

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AssignmentsConfig(AppConfig):
    """Конфигурация приложения assignments."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.assignments"
    label = "assignments"
    verbose_name = _("Задания и оценивание")

    def ready(self) -> None:
        """Инициализирует обработчики приложения при запуске."""
        with suppress(ModuleNotFoundError):
            import_module("apps.assignments.signals")
