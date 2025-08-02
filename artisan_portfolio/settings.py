from pathlib import Path
import os

from django.conf import settings

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-5=)0djqyf^0=k2q#0kxrs_b(f7yl*3*kxl&i+4n69vx#u44(u$'

DEBUG = True

ALLOWED_HOSTS = ['*']  # Temporaire pour le développement

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_countries',
    'main',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'artisan_portfolio.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'main/templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'main.context_processors.site_url',  # Ajout pour le contexte global
            ],
        },
    },
]

WSGI_APPLICATION = 'artisan_portfolio.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'fr-fr'

TIME_ZONE = 'Africa/Casablanca'

USE_I18N = True
USE_L10N = True
USE_TZ = True

# settings.py
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),  # Directement le dossier static
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Pour collectstatic

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# Paramètres email (exemple pour Mailjet)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'in-v3.mailjet.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'votre_api_key'  # Remplacez par votre clé API Mailjet
EMAIL_HOST_PASSWORD = 'votre_secret_key'  # Remplacez par votre secret key Mailjet
DEFAULT_FROM_EMAIL = 'contact@votresite.com'  # Email d'envoi par défaut

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuration personnalisée
SITE_URL = 'http://127.0.0.1:8000'  # À changer en production
SITE_NAME = 'Artisan Portfolio'

# Email Configuration (pour les futures fonctionnalités)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
icon_path = os.path.join(settings.BASE_DIR, "static/icons/phone.png")
# In settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'your-smtp-host'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@example.com'
EMAIL_HOST_PASSWORD = 'your-email-password'
DEFAULT_FROM_EMAIL = 'your-email@example.com'