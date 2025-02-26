import os
from pathlib import Path
from .config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER, ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, SECRET_KEY_ENV, CELERY_BROKER_URL_ENV, DEBUG_BOOL

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = SECRET_KEY_ENV

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = DEBUG_BOOL

ALLOWED_HOSTS = [ALLOWED_HOSTS, 'localhost', '127.0.0.1', '0.0.0.0']
CSRF_TRUSTED_ORIGINS = [CSRF_TRUSTED_ORIGINS]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Подключение сторонних приложений
    'simple_history',
    # Подключение приложений
    'main',
    'clients',
    'products',
    'take',
    'report',
    'config',
    'branch',
    'user',
    'telegram',
    'notifications'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

ROOT_URLCONF = 'cargo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cargo.context_processors.site_name',
            ],
        },
    },
]

WSGI_APPLICATION = 'cargo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }
DATABASES = {

    'default': {

        #'ENGINE': 'django.db.backends.sqlite3',

        'ENGINE': 'django.db.backends.postgresql',

        'NAME': DB_NAME,

        'USER': DB_USER,

        'PASSWORD': DB_PASS,

        'HOST': DB_HOST,

        'PORT': DB_PORT,

    }

}




# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Asia/Bishkek'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'main/static'),  # Только кастомная статика
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


LOGIN_URL = '/login/'  # Укажите путь к странице входа

CELERY_BROKER_URL = CELERY_BROKER_URL_ENV

# Настройка ID пользователя в истории
SIMPLE_HISTORY_HISTORY_USER_ID_FIELD = 'id'

MEDIA_URL = '/image/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')