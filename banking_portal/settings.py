import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# ——————————————————————————————————————————————————————————————
# Basis-Pfade und Umgebungsvariablen
# ——————————————————————————————————————————————————————————————
BASE_DIR = Path(__file__).resolve().parent.parent

# .env im Projekt-Root laden (lokal/CI)
env_file = BASE_DIR / '.env'
if env_file.exists():
    load_dotenv(env_file)

# ——————————————————————————————————————————————————————————————
# Sicherheits- und Debug-Einstellungen
# ——————————————————————————————————————————————————————————————
SECRET_KEY   = os.getenv('SECRET_KEY', 'dev-secret-key')
DEBUG        = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['*'] if DEBUG else os.getenv('ALLOWED_HOSTS', '').split(',')

# ——————————————————————————————————————————————————————————————
# Apps & Middleware
# ——————————————————————————————————————————————————————————————
INSTALLED_APPS = [
    # Sessions, Messages, Staticfiles
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Auth & ContentTypes (wichtig für Context Processors)
    'django.contrib.auth',
    'django.contrib.contenttypes',

    # Eigene App
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
]

ROOT_URLCONF = 'banking_portal.urls'

# ——————————————————————————————————————————————————————————————
# Templates & Context Processors
# ——————————————————————————————————————————————————————————————
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'core' / 'templates'],
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

WSGI_APPLICATION = 'banking_portal.wsgi.application'

# ——————————————————————————————————————————————————————————————
# Datenbank-Konfiguration (externe PostgreSQL via DATABASE_URL)
# ——————————————————————————————————————————————————————————————
DB_URL = os.getenv('DATABASE_URL')
if not DB_URL:
    raise RuntimeError(
        "DATABASE_URL ist nicht gesetzt! Bitte in den Environment-Variablen konfigurieren."
    )

DATABASES = {
    'default': dj_database_url.parse(
        DB_URL,
        conn_max_age=600,
        ssl_require=not DEBUG
    )
}

# ——————————————————————————————————————————————————————————————
# Statische Dateien
# ——————————————————————————————————————————————————————————————
STATIC_URL  = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
