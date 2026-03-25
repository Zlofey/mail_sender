from .settings import *  # noqa: F401,F403

# Override settings for testing
CELERY_BROKER_URL = None
CELERY_RESULT_BACKEND = None

# in-memory database instead of celery
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Disable logging for cleaner test output
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
}
