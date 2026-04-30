from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AssignmentsConfig(AppConfig):
    """Конфигурация приложения assignments."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.assignments'
    label = 'assignments'
    verbose_name = _("Задания и оценивание")

    def ready(self):
        """Инициализирует обработчики приложения при запуске."""
        try:
            import assignments.signals
        except ImportError:
            pass
