from pathlib import Path
import os
from dotenv import load_dotenv
import datetime 
import logging
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'emergencysystem.up.railway.app', 'ausecour.vercel.app', 'helpnext.vercel.app']


# Application definition

INSTALLED_APPS = [
    'whitenoise.runserver_nostatic',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_beat',
    'django_celery_results',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'rest_framework.authtoken',
    # 'django_ratelimit',
    'rest_auth',
    'corsheaders',
    'drf_yasg',
    
    'account',
]

SITE_ID=1

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTH_USER_MODEL="account.AbstractUserProfile"


AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "EmergencyBackend.backends.EmailOrPhoneBackend",
]

REDIS_URL = os.environ.get("REDIS_CONNECT")

CELERY_BROKER_URL =  REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
# CELERY CONFIG
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND")
CELERY_BEAT_SCHEDULER = os.environ.get("CELERY_BEAT_SCHEDULER")
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# REDIS CACHE CONFIG
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    },
    "ratelimit": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
    },
}
RATELIMIT_USE_CACHE = 'ratelimit'

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {  
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}


ROOT_URLCONF = 'EmergencyBackend.urls'

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

WSGI_APPLICATION = 'EmergencyBackend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.parse(os.getenv('PGCONNECT')),
    #     {
    #     'ENGINE': 'django.db.backends.sqlite3',
    #     'NAME': BASE_DIR / 'db.sqlite3',
    # }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOWED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'https://emergencysystem.up.railway.app',
    'https://ausecour.vercel.app',
    'https://helpnext.vercel.app',
]

SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTOCOL", "https")
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 31536000  
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
CORS_ALLOW_CREDENTIALS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
CSRF_HEADER_NAME = "X_CSRFToken"
# CSRF_COOKIE_NAME = 'csrftoken'
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://emergencysystem.up.railway.app',
    'https://ausecour.vercel.app',
    'https://helpnext.vercel.app',
    
]

CORS_ALLOW_HEADERS = [
    "access-control-allow-origin",
    "authorization",
    "content-type",
    "withcredentials",
]

CORS_ALLOW_ALL_ORIGINS = False

CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": [
            "'self'", 
            "https://emergencysystem.up.railway.app", 
            # "https://paqsstoragebucket.s3.amazonaws.com"
        ],
        "script-src": [
            "'self'", 
            "'unsafe-eval'",  
            "https://emergencysystem.up.railway.app", 
            # "https://paqsstoragebucket.s3.amazonaws.com",
            "'blob:'"
        ],
        "script-src-elem": [
            "'self'", 
            "'unsafe-eval'", 
            "https://emergencysystem.up.railway.app", 
            # "https://paqsstoragebucket.s3.amazonaws.com", 
        ],
        "style-src": [
            "'self'", 
            "https://paqscompany.vercel.app", 
            # "https://paqsstoragebucket.s3.amazonaws.com", 
            "'unsafe-inline'"  # allows inline CSS, useful if you have inline styles
        ],
        "style-src-elem": [
            "'self'",  
            # "https://paqsstoragebucket.s3.amazonaws.com", 
            "'unsafe-inline'"
        ],
        "connect-src": [
            "'self'", 
            "https://emergencysystem.up.railway.app", 
            # "https://paqsstoragebucket.s3.amazonaws.com"
        ],
        "img-src": [
            "'self'", 
            "blob:", 
            "data:", 
            "https://emergencysystem.up.railway.app", 
            # "https://paqsstoragebucket.s3.amazonaws.com"
        ],
        "font-src": [
            "'self'", 
            # "https://paqsstoragebucket.s3.amazonaws.com"
        ],
        "object-src": ["'none'"],
        "frame-ancestors": ["'self'"],
        "form-action": ["'self'"],
        "base-uri": ["'self'"],
        # "report-uri": "https://paqscompany.vercel.app/account/csp-report/",
        "upgrade-insecure-requests": True,
    },
}


WIGAL_KEY = os.environ.get("API_KEY")
WIGAL_SENDER_ID = os.environ.get("SENDER_ID")

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587

DEFAULT_FROM_EMAIL = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
PAYSTACK_PUBLIC_KEY = os.getenv("PAYSTACK_PUBLIC_KEY")

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')


OTP_EXPIRATION_TIME = 300

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'NON_FIELD_ERRORS_KEY': 'error',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(minutes=3),
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JSON_ENCODER': None,
    'JWK_URL': None,
    'LEEWAY': datetime.timedelta(seconds=30),

    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
}
