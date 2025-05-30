"""
Django settings for authback project.

Generated by 'django-admin startproject' using Django 5.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

from pathlib import Path
from decouple import config
from datetime import timedelta  # Add this import for JWT settings
import os
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-4ga9@g3zft*$zk1rwdu_au@v!w&zjfd%jodqv92=*s!2_x5r&r')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    'repairmybike.up.railway.app',
    'localhost',
    '127.0.0.1',
    '.railway.app',
]


# Application definition

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
    'accounts',
    'corsheaders',
    'marketplace',
    'django_filters',
    'vehicle',
    'repairing_service',
    
    # 'django_extens
    # ions'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Add this as the first middleware
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this after security middleware
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Service Ports Configuration
SERVICE_PORTS = {
    'API_GATEWAY': 8080,
    'DJANGO_SERVER': 8000,
    'FRONTEND_VITE': 5173,
    'FRONTEND_REACT': 3000,
    'REDIS': 6379,
    'POSTGRES': 5432,
    'CELERY_FLOWER': 5555,
}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    f"http://localhost:{SERVICE_PORTS['FRONTEND_VITE']}",  # Vite
    f"http://127.0.0.1:{SERVICE_PORTS['FRONTEND_VITE']}",
    f"http://localhost:{SERVICE_PORTS['FRONTEND_REACT']}",  # React
    f"http://127.0.0.1:{SERVICE_PORTS['FRONTEND_REACT']}",
    f"http://localhost:{SERVICE_PORTS['DJANGO_SERVER']}",  # Django
    f"http://127.0.0.1:{SERVICE_PORTS['DJANGO_SERVER']}",
    f"http://localhost:{SERVICE_PORTS['API_GATEWAY']}",  # API Gateway
    f"http://127.0.0.1:{SERVICE_PORTS['API_GATEWAY']}",
    "https://repairmybike.up.railway.app",  # Railway.app domain
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True  # Only for development
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
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
    'access-control-allow-origin',
]

ROOT_URLCONF = 'authback.urls'

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

WSGI_APPLICATION = 'authback.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases



# POSTGRES_LOCALLY = config("POSTGRES_LOCALLY", default=False, cast=bool)
# ENVIRONMENT = config("ENVIRONMENT", default="local")

# if ENVIRONMENT == 'production' or POSTGRES_LOCALLY:
#     DATABASES = {
#         'default': dj_database_url.parse(config('DATABASE_URL'))
#     }
# else:
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": config('DATABASE_NAME', default='rmbdevserver'),
        "USER": config('DATABASE_USER', default='postgres'),
        "PASSWORD": config('DATABASE_PASSWORD', default='mypassword'),
        "HOST": config('DATABASE_HOST', default='127.0.0.1'),
        "PORT": config('DATABASE_PORT', default=str(SERVICE_PORTS['POSTGRES'])),
    }
}

DATABASES_URL = config('DATABASE_URL', default='',cast=str)
if DATABASES_URL:
    import dj_database_url
    if DATABASES_URL.startswith('postgres://')or DATABASES_URL.startswith('postgresql://'):
        DATABASES = {
            'default': dj_database_url.config(
                default=DATABASES_URL,
            )
        }

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_ROOT = 'staticfiles'
STATIC_URL = '/static/'

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR,'staticfiles')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "rmbstatic/static")
]

MEDIA_ROOT =  os.path.join(BASE_DIR, 'public/static') 
MEDIA_URL = '/media/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.User'



LOGIN_REDIRECT_URL = '/login/success/'


# Security Settings - Disabled for development
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # Commented out for development
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
CSRF_TRUSTED_ORIGINS = [
    f"http://localhost:{SERVICE_PORTS['FRONTEND_VITE']}",
    'https://repairmybike.up.railway.app',
]
# Rate Limiting Settings
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'
RATELIMIT_KEY_PREFIX = 'ratelimit'
RATELIMIT_BLOCK = True
RATELIMIT_VIEW = 'accounts.views.rate_limit_view'

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
} if not config('USE_REDIS', default=False, cast=bool) else {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_PUBLIC_URL', default=f'redis://127.0.0.1:{SERVICE_PORTS["REDIS"]}/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'RETRY_ON_TIMEOUT': True,
            'MAX_CONNECTIONS': 100,
            'CONNECTION_POOL_KWARGS': {'max_connections': 100},
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'IGNORE_EXCEPTIONS': True,
        },
        'KEY_PREFIX': 'authback',
    }
}

# Cache timeout settings
CACHE_TTL = 60 * 5  # Cache timeout of 5 minutes
CACHE_MIDDLEWARE_SECONDS = 60 * 5  # Cache middleware timeout of 5 minutes

# Redis as the cache backend
DJANGO_REDIS_IGNORE_EXCEPTIONS = True
DJANGO_REDIS_LOG_IGNORED_EXCEPTIONS = True

# JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # More permissive for development
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'EXCEPTION_HANDLER': 'rest_framework.views.exception_handler',
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
}






CELERY_BROKER_URL = config('CELERY_BROKER_URL', default=f'redis://localhost:{SERVICE_PORTS["REDIS"]}/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default=f'redis://localhost:{SERVICE_PORTS["REDIS"]}/1')
CELERY_FLOWER_PORT = SERVICE_PORTS['CELERY_FLOWER']




EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.hostinger.com'  # Use your email provider's SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')  # Add this in your .env file
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')  # Add this in your .env file
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')  # Add this in your .env file

# Authentication backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]