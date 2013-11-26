#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    sys.path.append('../..') # Allow us to access test Django applications
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django1_6.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
