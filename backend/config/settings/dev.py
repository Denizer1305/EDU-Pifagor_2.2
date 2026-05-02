from __future__ import annotations

# ruff: noqa: F403, F405
from .base import *

DEBUG = True

SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    env("SECRET_KEY", "unsafe-local-dev-secret-key"),
)

ALLOWED_HOSTS = env_list(
    "DJANGO_ALLOWED_HOSTS",
    "127.0.0.1,localhost,0.0.0.0",
)

USE_POSTGRES_FOR_DEV = env_bool("USE_POSTGRES_FOR_DEV", False)

if USE_POSTGRES_FOR_DEV:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("POSTGRES_DB", "pifagor_dev"),
            "USER": env("POSTGRES_USER", "pifagor"),
            "PASSWORD": env("POSTGRES_PASSWORD", "pifagor"),
            "HOST": env("DB_HOST", "localhost"),
            "PORT": env("DB_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

CORS_ALLOWED_ORIGINS = env_list(
    "CORS_ALLOWED_ORIGINS",
    ",".join(
        [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:8080",
            "http://127.0.0.1:8080",
        ]
    ),
)

CSRF_TRUSTED_ORIGINS = env_list(
    "CSRF_TRUSTED_ORIGINS",
    ",".join(
        [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:8080",
            "http://127.0.0.1:8080",
        ]
    ),
)

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

SECURE_SSL_REDIRECT = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

LOGGING["root"]["level"] = "INFO"
LOGGING["loggers"]["django"]["level"] = "INFO"
LOGGING["loggers"]["django.db.backends"]["level"] = "WARNING"
LOGGING["loggers"]["apps"]["level"] = "DEBUG"

ENABLE_DEBUG_TOOLBAR = env_bool("ENABLE_DEBUG_TOOLBAR", True)

if ENABLE_DEBUG_TOOLBAR:
    INSTALLED_APPS += [
        "debug_toolbar",
    ]

    MIDDLEWARE.insert(
        1,
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    )

    INTERNAL_IPS = [
        "127.0.0.1",
        "localhost",
    ]
