import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

@pytest.fixture
def api_client():
    """Return an authenticated API client."""
    return APIClient()

@pytest.fixture
def create_user():
    """Factory to create test users."""
    def _create_user(username="testuser", email="test@example.com", password="password123"):
        return User.objects.create_user(username=username, email=email, password=password)
    return _create_user

@pytest.fixture
def auth_client(create_user):
    """Return an authenticated API client."""
    user = create_user()
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client, user

@pytest.fixture
def sample_job_application_data():
    """Return sample data for creating a job application."""
    return {
        'company_name': 'Test Company',
        'job_title': 'Software Engineer',
        'job_description': 'A job description for testing purposes.',
        'location': 'Remote',
        'salary_min': '80000.00',
        'salary_max': '120000.00',
        'remote_status': 'FULLY_REMOTE',
        'job_posting_url': 'https://example.com/job'
    }
