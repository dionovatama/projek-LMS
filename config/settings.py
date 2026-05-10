"""
Django settings for config project.
"""

from pathlib import Path
import os
from decouple import config, Csv
from datetime import timedelta

# ==============================================================
# BASE DIR
# ==============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================
# SECURITY
# ==============================================================

SECRET_KEY = config('SECRET_KEY')

DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='127.0.0.1,localhost',
    cast=Csv()
)

CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='http://127.0.0.1,http://localhost',
    cast=Csv()
)

# ==============================================================
# APPLICATIONS
# ==============================================================

INSTALLED_APPS = [
    # Django Default
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Local Apps
    'learning',
    'accounts',
]

# ==============================================================
# MIDDLEWARE
# ==============================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',

    'django.middleware.common.CommonMiddleware',

    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',

    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ==============================================================
# URL & WSGI
# ==============================================================

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

# ==============================================================
# TEMPLATE
# ==============================================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        'DIRS': [
            BASE_DIR / 'templates'
        ],

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

# ==============================================================
# DATABASE
# ==============================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',

        'NAME': config(
            'DB_NAME',
            default='elearning_db'
        ),

        'USER': config(
            'DB_USER',
            default='postgres'
        ),

        'PASSWORD': config(
            'DB_PASSWORD',
            default=''
        ),

        'HOST': config(
            'DB_HOST',
            default='127.0.0.1'
        ),

        'PORT': config(
            'DB_PORT',
            default='5432'
        ),
    }
}

# ==============================================================
# AUTH USER
# ==============================================================

AUTH_USER_MODEL = 'learning.CustomUser'

# ==============================================================
# PASSWORD VALIDATION
# ==============================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },

    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8
        }
    },

    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },

    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ==============================================================
# INTERNATIONALIZATION
# ==============================================================

LANGUAGE_CODE = 'id'

TIME_ZONE = 'Asia/Jakarta'

USE_I18N = True

USE_TZ = True

# ==============================================================
# STATIC FILES
# ==============================================================

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'learning' / 'static'
]

STATIC_ROOT = BASE_DIR / 'staticfiles'

# ==============================================================
# MEDIA FILES
# ==============================================================

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'

# ==============================================================
# DEFAULT PRIMARY KEY
# ==============================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==============================================================
# SECURITY HEADERS
# ==============================================================

SECURE_CONTENT_TYPE_NOSNIFF = True

X_FRAME_OPTIONS = 'DENY'

SECURE_REFERRER_POLICY = 'same-origin'

# ==============================================================
# HTTP MODE (sementara development/internal)
# ==============================================================

if DEBUG:
    SECURE_SSL_REDIRECT = False

    SESSION_COOKIE_SECURE = False

    CSRF_COOKIE_SECURE = False

# ==============================================================
# HTTPS MODE (production)
# ==============================================================

else:
    SECURE_SSL_REDIRECT = True

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True

    SECURE_PROXY_SSL_HEADER = (
        'HTTP_X_FORWARDED_PROTO',
        'https'
    )

    SECURE_HSTS_SECONDS = 3600

    SECURE_HSTS_INCLUDE_SUBDOMAINS = True

    SECURE_HSTS_PRELOAD = True

# ==============================================================
# LOGGING
# ==============================================================

LOGGING = {
    'version': 1,

    'disable_existing_loggers': False,

    'formatters': {
        'verbose': {
            'format': (
                '[{asctime}] '
                '{levelname} '
                '{name} '
                '{message}'
            ),
            'style': '{',
        },
    },

    'handlers': {
        'file': {
            'level': 'WARNING',

            'class': 'logging.FileHandler',

            'filename': BASE_DIR / 'warning.log',

            'formatter': 'verbose',
        },
    },

    'loggers': {
        'django': {
            'handlers': ['file'],

            'level': 'WARNING',

            'propagate': True,
        },
    },
}