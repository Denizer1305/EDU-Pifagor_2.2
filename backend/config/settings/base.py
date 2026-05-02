from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

# Путь к основному каталогу проекта
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Загружаем переменные окружения из .env
load_dotenv(BASE_DIR / ".env")


def env(name: str, default: str | None = None, *, required: bool = False) -> str:
    """Функция для извлечения переменных окружения с поддержкой обязательных значений."""
    value = os.getenv(name, default)
    if required and not value:
        raise RuntimeError(
            f"Переменная окружения {name} обязательна для работы приложения."
        )
    return value


# SECRET_KEY теперь обязательно должен быть задан в переменных окружения
SECRET_KEY = env("DJANGO_SECRET_KEY", required=True)

# Включаем или отключаем debug-режим в зависимости от переменной окружения
DEBUG = env("DJANGO_DEBUG", "False") == "True"

# Список разрешённых хостов
ALLOWED_HOSTS = [
    host.strip()
    for host in env("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")
    if host.strip()
]

# Локализация
LANGUAGE_CODE = "ru"
TIME_ZONE = env("DJANGO_TIME_ZONE", "Europe/Moscow")

LANGUAGES = [
    ("ru", "Русский"),
    ("en", "English"),
]

LOCALE_PATHS = [
    BASE_DIR / "locale",
]

USE_I18N = True
USE_TZ = True

# Настройки для шаблонов
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",  # Папка для шаблонов
        ],
        "APP_DIRS": True,  # Для автоматического поиска шаблонов в приложениях
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Основная конфигурация базы данных PostgreSQL
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("POSTGRES_DB", required=True),
        "USER": env("POSTGRES_USER", required=True),
        "PASSWORD": env("POSTGRES_PASSWORD", required=True),
        "HOST": env("DB_HOST", "localhost"),
        "PORT": env("DB_PORT", "5432"),
    }
}

# Установленные приложения
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "django_filters",
    "drf_spectacular",
    "rest_framework",
    "apps.common.apps.CommonConfig",
    "apps.users.apps.UsersConfig",
    "apps.organizations.apps.OrganizationsConfig",
    "apps.education.apps.EducationConfig",
    "apps.course.apps.CoursesConfig",
    "apps.assignments.apps.AssignmentsConfig",
    "apps.feedback.apps.FeedbackConfig",
    "apps.journal.apps.JournalConfig",
]

# Мидлвары
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

# Конфигурация статических файлов
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Конфигурация медиа-файлов
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Основные настройки безопасности
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = env("DJANGO_SECURE_SSL_REDIRECT", "False") == "True"
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS", "https://example.com").split(",")

# Прочие настройки безопасности
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 365  # 1 год
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_REFERRER_POLICY = "same-origin"


log_dir = BASE_DIR / "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Логирование
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
    "loggers": {
        "django.db.backends": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        "apps.assignments": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}

# Настройки кеширования
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Конфигурация CORS (если API доступно из других доменов)
CORS_ALLOWED_ORIGINS = [
    "https://example.com",
]

ROOT_URLCONF = "config.urls"  # Это путь до файла urls.py в папке config

# Прочее
AUTH_USER_MODEL = "users.User"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
