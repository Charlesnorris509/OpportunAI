import pytest
from django.urls import reverse
from rest_framework import status
from applications.models import JobApplication

pytestmark = pytest.mark.django_db

class TestJobApplications:
    def test_create_application(self, auth_client, sample_job_application_data):
        """Test creating a job application."""
        client, user = auth_client
        url = reverse('job-application-list')
        
        response = client.post(url, sample_job_application_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert JobApplication.objects.filter(user=user).count() == 1
        assert response.data['company_name'] == sample_job_application_data['company_name']
        
    def test_list_applications(self, auth_client):
        """Test listing job applications."""
        client, user = auth_client
        # Create some test applications
        from TEST.utils import create_test_job_application
        create_test_job_application(user)
        create_test_job_application(user, {'company_name': 'Another Company', 'job_title': 'Designer'})
        
        url = reverse('job-application-list')
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2
        
    def test_update_application_status(self, auth_client):
        """Test updating job application status."""
        client, user = auth_client
        from TEST.utils import create_test_job_application
        application = create_test_job_application(user)
        
        url = reverse('job-application-update-status', args=[application.id])
        response = client.post(url, {'status': 'APPLIED'}, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        application.refresh_from_db()
        assert application.status == 'APPLIED'
        assert application.application_date is not None
