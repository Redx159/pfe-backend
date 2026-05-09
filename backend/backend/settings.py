"""
Django settings for backend project.
"""

import os
from pathlib import Path
from datetime import timedelta

# --------------------------------------------------
# BASE DIR
# --------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------
# SECURITY
# --------------------------------------------------
SECRET_KEY = 'django-insecure-2h69+_rfwb%tcs%c8rdnph*8%5tyfu)5fdulyi)_u6+-=8@+ex'

DEBUG = True
ALLOWED_HOSTS = ['*']

# --------------------------------------------------
# APPLICATIONS
# --------------------------------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',

    # Third-party
    'rest_framework',
    'corsheaders',
    'drf_spectacular',

    # Local apps
    'employees',
    'attendance',
    'leaves',
    "meetings",
    "assistantbot",
    "notifications",
    "analytics",
]

# --------------------------------------------------
# MIDDLEWARE
# --------------------------------------------------
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --------------------------------------------------
# URLS / WSGI
# --------------------------------------------------
ROOT_URLCONF = 'backend.urls'
WSGI_APPLICATION = 'backend.wsgi.application'

# --------------------------------------------------
# TEMPLATES
# --------------------------------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

# --------------------------------------------------
# DATABASE
# --------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'pfe',
        'USER': 'pfe_user',
        'PASSWORD': 'redxguessous2006',
        'HOST': 'localhost',
        'PORT': '1024',
    }
}


# --------------------------------------------------
# AUTH
# --------------------------------------------------
AUTH_USER_MODEL = 'employees.Employee'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --------------------------------------------------
# INTERNATIONALIZATION  ✅ FIXED
# --------------------------------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Casablanca'
USE_I18N = True
USE_TZ = True

# --------------------------------------------------
# STATIC & MEDIA FILES
# --------------------------------------------------
STATIC_URL = 'static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# --------------------------------------------------
# CACHING
# --------------------------------------------------
# For production, set CACHE_BACKEND to django_redis.cache.RedisCache
# and CACHE_LOCATION to redis://127.0.0.1:6379/1
# Requires: pip install django-redis
CACHES = {
    'default': {
        'BACKEND': os.environ.get(
            'CACHE_BACKEND',
            'django.core.cache.backends.locmem.LocMemCache',
        ),
        'LOCATION': os.environ.get('CACHE_LOCATION', 'unique-snowflake'),
        # Uncomment for Redis:
        # 'OPTIONS': {
        #     'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        #     'IGNORE_EXCEPTIONS': True,
        # },
    }
}
CACHE_TTL = int(os.environ.get('CACHE_TTL', 300))  # 5 min default

# --------------------------------------------------
# DRF SPECTACULAR (API Docs)
# --------------------------------------------------
SPECTACULAR_SETTINGS = {
    'TITLE': 'HR Management API',
    'DESCRIPTION': 'Full-stack HR management system — attendance, leaves, meetings, notifications',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# --------------------------------------------------
# CORS
# --------------------------------------------------
CORS_ALLOW_ALL_ORIGINS = True  # Override per-environment for production

# --------------------------------------------------
# DJANGO REST FRAMEWORK
# --------------------------------------------------
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '20/hour',
        'user': '200/hour',
    },
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
}

# --------------------------------------------------
# SIMPLE JWT  ✅ FIXED
# --------------------------------------------------
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Email configuration (prefer environment variables for secrets)
# By default emails are printed to the console for local development.
EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend'
)

# Default from address used when sending emails
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@example.com')

# If using SMTP backend, the following environment variables will be read:
# EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_USE_TLS
if EMAIL_BACKEND == 'django.core.mail.backends.smtp.EmailBackend':
    EMAIL_HOST = os.environ.get('EMAIL_HOST', 'sandbox.smtp.mailtrap.io')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 2525))
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '60fa0c89a54305')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '45cd39f65f1eeb')
    EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() in ('1', 'true', 'yes')

# --------------------------------------------------
# SECURITY HARDENING (production overrides via env)
# --------------------------------------------------
if not DEBUG:
    SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'True').lower() in ('1', 'true', 'yes')
    SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', 31536000))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = os.environ.get(
        'CORS_ALLOWED_ORIGINS',
        'https://localhost:3000,https://example.com',
    ).split(',')
