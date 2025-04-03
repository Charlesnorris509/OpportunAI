# OpportunAI - Automated Job Application System

This file contains instructions for testing and deploying the OpportunAI application.

## Testing Instructions

### Prerequisites
- Python 3.8+
- PostgreSQL database
- OpenAI API key

### Setup for Testing
1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with the following variables:
```
DEBUG=True
SECRET_KEY=your_secret_key
DATABASE_URL=postgres://user:password@localhost:5432/opportunai
OPENAI_API_KEY=your_openai_api_key
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

### Testing Core Functionality

#### 1. LinkedIn Job Search
- Navigate to `/linkedin/search/`
- Enter job search keywords (e.g., "software developer")
- Verify that job results are displayed correctly

#### 2. Resume Analysis
- Upload a resume in your profile settings
- Navigate to `/resume/analyze/`
- Verify that keywords are extracted correctly
- Test job match analysis with a specific job

#### 3. Cover Letter Generation
- Navigate to `/cover-letter/generate/<job_id>/`
- Verify that a tailored cover letter is generated based on your resume and the job description
- Test editing and downloading the cover letter

#### 4. Job Matching
- Navigate to `/job-matching/matches/`
- Verify that jobs are scored based on keyword matching with your resume
- Test finding new matches with different search criteria

#### 5. Automated Application
- Navigate to `/automation/schedules/create/`
- Create a schedule for automated applications
- Test running the schedule manually
- Verify that applications are submitted correctly

#### 6. Management Command
- Test the scheduled application command:
```bash
python manage.py run_scheduled_applications
```

## Deployment Instructions

### Prerequisites
- Server with Python 3.8+
- PostgreSQL database
- Nginx or Apache web server
- Supervisor or systemd for process management

### Deployment Steps

1. Clone the repository on your server:
```bash
git clone https://github.com/yourusername/opportunai.git
cd opportunai
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with production settings:
```
DEBUG=False
SECRET_KEY=your_secure_secret_key
DATABASE_URL=postgres://user:password@localhost:5432/opportunai_prod
OPENAI_API_KEY=your_openai_api_key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Collect static files:
```bash
python manage.py collectstatic
```

7. Configure Gunicorn:
Create a file named `gunicorn_start.sh`:
```bash
#!/bin/bash
NAME="opportunai"
DIR=/path/to/opportunai
USER=your_user
GROUP=your_group
WORKERS=3
BIND=unix:/path/to/opportunai/run/gunicorn.sock
DJANGO_SETTINGS_MODULE=job_tracker.settings
DJANGO_WSGI_MODULE=job_tracker.wsgi
LOG_LEVEL=error

cd $DIR
source venv/bin/activate

exec gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $WORKERS \
  --user=$USER \
  --group=$GROUP \
  --bind=$BIND \
  --log-level=$LOG_LEVEL \
  --log-file=-
```

8. Configure Supervisor:
Create a file named `/etc/supervisor/conf.d/opportunai.conf`:
```
[program:opportunai]
command=/path/to/opportunai/gunicorn_start.sh
user=your_user
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/path/to/opportunai/logs/gunicorn-error.log
```

9. Configure Nginx:
Create a file named `/etc/nginx/sites-available/opportunai`:
```
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /path/to/opportunai;
    }

    location /media/ {
        root /path/to/opportunai;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/path/to/opportunai/run/gunicorn.sock;
    }
}
```

10. Enable the site:
```bash
ln -s /etc/nginx/sites-available/opportunai /etc/nginx/sites-enabled
```

11. Set up SSL with Let's Encrypt:
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

12. Set up a cron job for automated applications:
```bash
crontab -e
```
Add the following line to run the scheduler every hour:
```
0 * * * * /path/to/opportunai/venv/bin/python /path/to/opportunai/manage.py run_scheduled_applications
```

13. Restart services:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart opportunai
sudo systemctl restart nginx
```

## Monitoring and Maintenance

1. Check application logs:
```bash
tail -f /path/to/opportunai/logs/gunicorn-error.log
```

2. Monitor automated application runs:
```bash
python manage.py shell
```
```python
from job_tracker.apps.automated_application.models import AutomatedApplicationRun
AutomatedApplicationRun.objects.all().order_by('-start_time')[:10]
```

3. Backup the database regularly:
```bash
pg_dump -U your_db_user opportunai_prod > opportunai_backup_$(date +%Y%m%d).sql
```

4. Update the application:
```bash
cd /path/to/opportunai
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo supervisorctl restart opportunai
```
