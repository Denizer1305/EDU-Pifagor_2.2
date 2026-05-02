from __future__ import annotations

import os

# ruff: noqa: F403, F405
from .base import *

DEBUG = False

SECRET_KEY = "test-secret-key"

ALLOWED_HOSTS = [
    "testserver",
    "localhost",
    "127.0.0.1",
]

USE_POSTGRES_FOR_TESTS = os.getenv("USE_POSTGRES_FOR_TESTS", "0") == "1"

if USE_POSTGRES_FOR_TESTS:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", "pifagor_test"),
            "USER": os.getenv("POSTGRES_USER", "pifagor"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", "pifagor"),
            "HOST": os.getenv("DB_HOST", "localhost"),
            "PORT": os.getenv("DB_PORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "test_db.sqlite3",
        }
    }

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

CORS_ALLOWED_ORIGINS = []
CSRF_TRUSTED_ORIGINS = []

SECURE_SSL_REDIRECT = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

LOGGING["root"]["level"] = "ERROR"
LOGGING["loggers"]["django"]["level"] = "ERROR"
LOGGING["loggers"]["django.request"]["level"] = "ERROR"
LOGGING["loggers"]["django.db.backends"]["level"] = "WARNING"
LOGGING["loggers"]["apps"]["level"] = "ERROR"
