
import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.getenv("SECRET_KEY","dev")
DEBUG = os.getenv("DEBUG","1")=="1"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS","*").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.users",
    "apps.courses",
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF="config.urls"
WSGI_APPLICATION="config.wsgi.application"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
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
DATABASES={
 'default':{
  'ENGINE':'django.db.backends.postgresql',
  'NAME':os.getenv("POSTGRES_DB"),
  'USER':os.getenv("POSTGRES_USER"),
  'PASSWORD':os.getenv("POSTGRES_PASSWORD"),
  'HOST':os.getenv("POSTGRES_HOST","db"),
  'PORT':os.getenv("POSTGRES_PORT","5432"),
 }
}
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}
STATIC_URL="/static/"
STATIC_ROOT=BASE_DIR/"staticfiles"
AUTH_USER_MODEL = "users.User"
from datetime import timedelta

SIMPLE_JWT = {

    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),

    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),

    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": True,

    "AUTH_HEADER_TYPES": ("Bearer",),

}