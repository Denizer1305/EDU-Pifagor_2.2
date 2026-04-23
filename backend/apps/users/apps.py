from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class UsersConfig(AppConfig):
    """Конфигурация приложения users."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    label = 'users'
    verbose_name = _("Пользователи")


    def ready(self):
        """Инициализирует обработчики приложения при запуске."""
        try:
            import users.signals
        except ImportError:
            pass
