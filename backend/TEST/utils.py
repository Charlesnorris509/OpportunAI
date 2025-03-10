from django.urls import reverse
import json

def get_jwt_token_for_user(client, username="testuser", password="password123"):
    """Helper function to get JWT token for a user."""
    url = reverse('auth_app:login')
    response = client.post(url, {
        'username': username,
        'password': password
    }, format='json')
    return json.loads(response.content)

def create_test_job_application(user, data=None):
    """Helper function to create a test job application."""
    from applications.models import JobApplication
    
    if data is None:
        data = {
            'company_name': 'Test Company',
            'job_title': 'Software Engineer',
            'job_description': 'A job description for testing.',
            'status': 'SAVED'
        }
    
    return JobApplication.objects.create(user=user, **data)
