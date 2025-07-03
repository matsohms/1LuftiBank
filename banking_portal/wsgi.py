import os
from django.core.wsgi import get_wsgi_application

# ENV-Settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking_portal.settings')

# WSGI-App erstellen
application = get_wsgi_application()

# Automatisch Datenbank-Migrationen und SyncDB-Mode beim Start
try:
    from django.core.management import call_command
    # Erst Migrationen anwenden (falls vorhanden)
    call_command('migrate', '--noinput', '--run-syncdb')
except Exception:
    pass
