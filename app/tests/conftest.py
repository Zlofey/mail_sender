import os
import django

# Set Django settings module for tests
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.test_settings")

# Setup Django
django.setup()
