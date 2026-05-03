from contextlib import suppress
from importlib import import_module

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class JournalConfig(AppConfig):
    """Конфигурация приложения journal."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.journal"
    label = "journal"
    verbose_name = _("Электронный журнал")

    def ready(self) -> None:
        """Инициализирует обработчики приложения при запуске."""
        with suppress(ModuleNotFoundError):
            import_module("apps.journal.signals")
