from .base import *

# Включаем режим отладки для продакшн-среды
DEBUG = False

# Используем PostgreSQL для продакшн
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

# Включаем настройки безопасности для продакшн
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 365  # 1 год
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Логирование для продакшн (ошибки записываем в файл)
LOGGING["loggers"]["django"]["handlers"] = ["console", "file"]
LOGGING["loggers"]["django"]["level"] = "ERROR"

# Настройки CORS для продакшн
CORS_ALLOWED_ORIGINS = [
    "https://example.com",  # Домен фронтенда в продакшн-среде
]

# Используем Redis для кеширования (можно использовать Memcached или другие варианты)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": env("REDIS_URL", "redis://127.0.0.1:6379/1"),
    }
}

# Почта для продакшн: Настроим реальный backend для отправки писем
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = env("EMAIL_PORT", "587")
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env("EMAIL_HOST_USER", required=True)
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", required=True)

# Настройки для статики и медиа-файлов
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Настройки безопасности: отключаем debug-toolbar в продакшн
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != "debug_toolbar"]
MIDDLEWARE = [
    mw for mw in MIDDLEWARE if mw != "debug_toolbar.middleware.DebugToolbarMiddleware"
]
