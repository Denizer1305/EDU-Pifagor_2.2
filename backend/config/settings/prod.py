from __future__ import annotations

from .base import *

DEBUG = False

SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    env("SECRET_KEY"),
    required=True,
)

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS")

if not ALLOWED_HOSTS:
    raise RuntimeError(
        "Переменная окружения DJANGO_ALLOWED_HOSTS обязательна для production."
    )

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB", required=True),
        "USER": env("POSTGRES_USER", required=True),
        "PASSWORD": env("POSTGRES_PASSWORD", required=True),
        "HOST": env("DB_HOST", "localhost"),
        "PORT": env("DB_PORT", "5432"),
        "CONN_MAX_AGE": env_int("DB_CONN_MAX_AGE", 60),
    }
}

CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS")
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")

SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", True)
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

SECURE_HSTS_SECONDS = env_int(
    "DJANGO_SECURE_HSTS_SECONDS",
    60 * 60 * 24 * 365,
)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool(
    "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS",
    True,
)

SECURE_HSTS_PRELOAD = env_bool(
    "DJANGO_SECURE_HSTS_PRELOAD",
    False,
)

SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env("REDIS_URL", "redis://127.0.0.1:6379/1"),
    }
}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", required=True)
EMAIL_PORT = env_int("EMAIL_PORT", 587)
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", required=True)
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", required=True)
DEFAULT_FROM_EMAIL = env(
    "DEFAULT_FROM_EMAIL",
    f"Pifagor <{EMAIL_HOST_USER}>",
)

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOGGING["handlers"]["file"] = {
    "class": "logging.handlers.RotatingFileHandler",
    "filename": LOG_DIR / "django.log",
    "maxBytes": 1024 * 1024 * 10,
    "backupCount": 5,
    "formatter": "verbose",
    "encoding": "utf-8",
}

LOGGING["root"]["handlers"] = ["console", "file"]
LOGGING["root"]["level"] = "WARNING"

LOGGING["loggers"]["django"]["handlers"] = ["console", "file"]
LOGGING["loggers"]["django"]["level"] = "ERROR"

LOGGING["loggers"]["django.request"]["handlers"] = ["console", "file"]
LOGGING["loggers"]["django.request"]["level"] = "ERROR"

LOGGING["loggers"]["apps"]["handlers"] = ["console", "file"]
LOGGING["loggers"]["apps"]["level"] = "INFO"
