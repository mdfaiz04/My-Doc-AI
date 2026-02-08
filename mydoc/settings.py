"""
Django settings for mydoc project.
"""

import os
from pathlib import Path

# ---------------------------
# ENVIRONMENT VARIABLE SETUP
# ---------------------------

# You imported BOTH python-decouple and django-environ previously.
# We will ONLY use django-environ because your code uses env()
# (env("MONGO_URI"), env("ADMIN_USERNAME"), etc.)
#
# So: KEEP environ, REMOVE python-decouple usage.

import environ
env = environ.Env()

# ---------------------------
# BASE SETTINGS
# ---------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(BASE_DIR / ".env")   # reads .env from project root

# Secrets come from .env (see .env.example) — never hard-code them here.
OLLAMA_API_KEY = env("OLLAMA_API_KEY", default="")
OLLAMA_API_BASE_URL = "https://ollama.com/v1/chat/completions"

SECRET_KEY = env("DJANGO_SECRET_KEY", default="django-insecure-dev-only-change-me")

DEBUG = env.bool("DEBUG", default=True)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

# ---------------------------
# INSTALLED APPS
# ---------------------------

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Your app (important!)
    'doctor',
]

# ---------------------------
# MIDDLEWARE
# ---------------------------

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ---------------------------
# URL & TEMPLATES
# ---------------------------

ROOT_URLCONF = 'mydoc.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mydoc.wsgi.application'


# ---------------------------
# DATABASE (Django ℹ️)
# Keep SQLite — do NOT remove or modify
# ---------------------------

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ---------------------------
# MONGO SETTINGS (Correct)
# ---------------------------

MONGO_URI = env("MONGO_URI", default="mongodb://localhost:27017")
MONGO_DB_NAME = env("MONGO_DB_NAME", default="doctor_app")

ADMIN_USERNAME = env("ADMIN_USERNAME", default="admin")
ADMIN_PASSWORD = env("ADMIN_PASSWORD", default="admin123")

# ---------------------------
# PASSWORD VALIDATION
# ---------------------------

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ---------------------------
# INTERNATIONALIZATION
# ---------------------------

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ---------------------------
# STATIC FILES
# ---------------------------

STATIC_URL = 'static/'

# Fix duplicate STATICFILES_DIRS
STATICFILES_DIRS = [
    BASE_DIR / "static"
]

STATIC_ROOT = BASE_DIR / "staticfiles"

# ---------------------------
# DEFAULT PRIMARY KEY TYPE
# ---------------------------

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
