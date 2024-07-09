#!/bin/env python3
import os

from django.core.management import django, call_command

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nfstats.settings")
django.setup()

from django.contrib.auth.models import User

# Creating superuser
if not User.objects.filter(is_superuser=True).exists():
    call_command("createsuperuser", "--noinput")
    print("Superuser created successfully.")
else:
    print("Superuser already exists.")
