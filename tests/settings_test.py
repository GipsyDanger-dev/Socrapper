"""
Test settings for Socrapper.

Forces SQLite (no external database server needed) and disables the LLM so
the test suite stays offline, fast, and deterministic — regardless of the
project .env, which may point at PostgreSQL and a real LLM provider.
"""

from socrapper.settings import *  # noqa: F401,F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Never call the real LLM from tests
LLM_API_KEY = ""
LLM_BASE_URL = ""
LLM_MODEL = "test-model"
