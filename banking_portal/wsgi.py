import os
from django.core.wsgi import get_wsgi_application

# ENV-Settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking_portal.settings')

# WSGI-App erstellen
application = get_wsgi_application()

# Automatisch Datenbank-Migrationen ausführen (Session- & Core-Model-Tabellen)
try:
    from django.core.management import call_command
    call_command('makemigrations', '--noinput')
    call_command('migrate', '--noinput')
except Exception:
    # Fehler ignorieren, falls schon migriert oder im Production nicht gewünscht
    pass
