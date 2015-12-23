# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from django.contrib import messages

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'djangobower',
    'app',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'app.middleware.SocialBinderMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'), ],
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

WSGI_APPLICATION = 'wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'djangobower.finders.BowerFinder',
)

STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

# Bower components
BOWER_COMPONENTS_ROOT = os.path.join(PROJECT_ROOT)

BOWER_INSTALLED_APPS = (
    'jquery',
    'bootstrap',
    'fontawesome',
    'angular'
    'angular-moment',
    'angular-animate',
    'ng-file-upload',
    'slick-carousel',
)

# Facebook credentials
FB_APP_ID = os.getenv('FB_APP_ID')

FB_APP_NAME = os.getenv('FB_APP_NAME')

FB_APP_SECRET = os.getenv('FB_APP_SECRET')

FB_SCOPE = ('email', 'public_profile', 'publish_actions',)

AUTH_USER_MODEL = 'app.SocialUser'

# Custom class for messages
MESSAGE_TAGS = {
    messages.ERROR: 'danger'
}

# Photo Filters
PHOTO_FX_BASIC = (
    'Alien',
    'Blur',
    'Blur More',
    'Brighten',
    'Contour',
    'Detail',
    'Edge',
    'Edge Enhance',
    'Edge Enhance More',
    'Emboss',
    'Find Edges',
    'Smooth',
    'Smooth More',
    'Sharpen',
    'Sharpen More',
)

PHOTO_FX_ADVANCED = (
    'Sepia',
    'Whoops',
    'Grayscale',
)

MEDIA_URL = '/'

MEDIA_ROOT = 'photo_editor'

# Max file size 10MB
MAX_UPLOAD_SIZE = 10485760
