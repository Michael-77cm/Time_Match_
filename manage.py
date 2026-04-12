#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Ensure this project directory is first in sys.path.
    current_path = os.path.dirname(os.path.abspath(__file__))
    if current_path in sys.path:
        sys.path.remove(current_path)
    sys.path.insert(0, current_path)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'timematch.settings')
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
