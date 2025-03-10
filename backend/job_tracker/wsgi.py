# 4. backend/job_tracker/wsgi.py
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_tracker.settings')
application = get_wsgi_application()
