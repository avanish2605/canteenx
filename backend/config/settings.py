from pathlib import Path
from datetime import timedelta
from decouple import config, Csv
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-canteenx-dev-key-change-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1,testserver,.onrender.com,*', cast=Csv())

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'accounts',
    'canteens',
    'menu',
    'cart',
    'orders',
    'notifications',
    'analytics',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

AUTH_USER_MODEL = 'accounts.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.vercel\.app$",
    r"^https://.*\.onrender\.com$",
    r"^http://localhost:[0-9]+$",
    r"^http://127\.0\.0\.1:[0-9]+$",
]
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]
frontend_url_cfg = config('FRONTEND_URL', default='http://127.0.0.1:5173')
if frontend_url_cfg and frontend_url_cfg not in CORS_ALLOWED_ORIGINS:
    CORS_ALLOWED_ORIGINS.append(frontend_url_cfg)

CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='http://localhost:5173,http://127.0.0.1:5173,https://*.onrender.com,https://*.vercel.app',
    cast=Csv()
)
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

database_url = config('DATABASE_URL', default=None)
if database_url:
    DATABASES = {
        'default': dj_database_url.config(
            default=database_url,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ──────────────────────────────────────────────────────────────────────────────
# Email Configuration
# python-decouple reads from .env automatically — os.getenv() does NOT.
# EMAIL_BACKEND auto-selects SMTP when EMAIL_HOST_USER is set, console otherwise.
# ──────────────────────────────────────────────────────────────────────────────
_email_host_user = config('EMAIL_HOST_USER', default='')
_email_host_password = config('EMAIL_HOST_PASSWORD', default='')

EMAIL_BACKEND = config(
    'EMAIL_BACKEND',
    default=(
        'django.core.mail.backends.smtp.EmailBackend'
        if (_email_host_user and _email_host_password)
        else 'django.core.mail.backends.console.EmailBackend'
    )
)
EMAIL_HOST          = config('EMAIL_HOST',      default='smtp.gmail.com')
EMAIL_PORT          = config('EMAIL_PORT',      default=587, cast=int)
EMAIL_USE_TLS       = config('EMAIL_USE_TLS',   default=True, cast=bool)
EMAIL_HOST_USER     = _email_host_user
EMAIL_HOST_PASSWORD = _email_host_password
EMAIL_TIMEOUT       = config('EMAIL_TIMEOUT',   default=5, cast=int)

# Resend HTTP API support (Bypasses cloud provider port 587/465 blocks over HTTPS port 443)
RESEND_API_KEY      = config('RESEND_API_KEY', default='')
RESEND_FROM_EMAIL   = config('RESEND_FROM_EMAIL', default='CanteenX <onboarding@resend.dev>')

# Brevo HTTP API support (Bypasses cloud provider port blocks, sends to ANY recipient without custom domain)
BREVO_API_KEY       = config('BREVO_API_KEY', default='')

# DEFAULT_FROM_EMAIL: when Gmail SMTP is used, the From address MUST match the
# authenticated account — otherwise Gmail rejects it. We auto-build it here.
_from_default = (
    f'CanteenX Medi-Caps <{_email_host_user}>'
    if _email_host_user
    else 'CanteenX Medi-Caps <canteenx@medicaps.ac.in>'
)
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=_from_default)

# Frontend URL (for password reset links)
FRONTEND_URL = config('FRONTEND_URL', default='http://127.0.0.1:5173')

# WhatsApp Configuration (Twilio WhatsApp API)
TWILIO_ACCOUNT_SID   = config('TWILIO_ACCOUNT_SID',   default='')
TWILIO_AUTH_TOKEN    = config('TWILIO_AUTH_TOKEN',     default='')
TWILIO_WHATSAPP_FROM = config('TWILIO_WHATSAPP_FROM',  default='whatsapp:+14155238886')
