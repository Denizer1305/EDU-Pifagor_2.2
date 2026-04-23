from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class EducationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.education"
    label = "education"
    verbose_name = _("Образование")

    def ready(self):
        import apps.education.signals  # noqa: F401
