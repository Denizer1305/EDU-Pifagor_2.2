from .base import *

# Включаем режим отладки для разработки
DEBUG = True

# Используем SQLite для разработки
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Для разработки включаем шаблонные директории
TEMPLATES[0]["DIRS"] = [BASE_DIR / "templates"]

# Логирование для разработки (выводим все логи в консоль)
LOGGING["loggers"]["django"] = {
    "handlers": ["console"],
    "level": "INFO",
    "propagate": False,
}

# Включаем CORS для разработки (если фронтенд работает на другом порту)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Пример для Vue.js или React на локальном хосте
]

# Кэширование для разработки (локальное хранилище)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Можно включить почту для разработки
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Настройки для статики и медиа-файлов
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Включаем автоматическую перезагрузку сервера при изменении кода
INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
INTERNAL_IPS = ["127.0.0.1"]
