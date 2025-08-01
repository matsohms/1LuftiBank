import os, sys
from dotenv import load_dotenv
load_dotenv()

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'banking_portal.settings')
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
