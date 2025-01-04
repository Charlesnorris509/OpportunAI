#!/usr/bin/env python
import os
import sys
import logging
from dotenv import load_dotenv

def main():
    # Load environment variables from .env file
    load_dotenv()

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_tracker.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        logging.error("Couldn't import Django. Ensure it's installed and available on your PYTHONPATH environment variable. Did you forget to activate a virtual environment?")
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    main()
