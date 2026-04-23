from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class FeedbackConfig(AppConfig):
    """Конфигурация приложения users."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.feedback'
    label = 'feedback'
    verbose_name = _("Обратная связь")

    def ready(self):
        """Инициализирует обработчики приложения при запуске."""
        try:
            import feedback.signals
        except ImportError:
            pass
