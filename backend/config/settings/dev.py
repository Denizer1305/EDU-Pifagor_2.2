from .base import *

DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

if DB_ENGINE != "django.db.backends.sqlite3":
    DATABASES["default"]["HOST"] = os.getenv("DB_HOST", "127.0.0.1")
    DATABASES["default"]["PORT"] = os.getenv("DB_PORT", "5432")

EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
