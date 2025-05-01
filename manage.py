#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

#from .models import Annonce
#from django.contrib.auth.models import Group

# Crée le groupe Locataire s'il n'existe pas déjà
#locataire_group, created = Group.objects.get_or_create(name='Locataire')

# Tu peux vérifier si le groupe a bien été créé
#print(locataire_group)


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'immobilier.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
