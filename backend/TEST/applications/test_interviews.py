import pytest
from django.urls import reverse
from rest_framework import status
import datetime

pytestmark = pytest.mark.django_db

class TestInterviews:
    def test_schedule_interview(self, auth_client):
        """Test scheduling an interview for a job application."""
        client, user = auth_client
        # Create a job application first
        from TEST.utils import create_test_job_application
        application = create_test_job_application(user)
        
        url = reverse('interview-list')
        tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
        interview_data = {
            'application': application.id,
            'interview_type': 'PHONE',
            'date_time': tomorrow.isoformat(),
            'location': 'Phone call',
            'interviewer_names': 'John Doe',
            'notes': 'Prepare for technical questions'
        }
        
        response = client.post(url, interview_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['interview_type'] == 'PHONE'
        
        # Check if application status was updated to INTERVIEWING
        application.refresh_from_db()
        assert application.status == 'INTERVIEWING'
        
    def test_list_interviews(self, auth_client):
        """Test listing interviews for a job application."""
        client, user = auth_client
        # Create a job application and interviews
        from TEST.utils import create_test_job_application
        from applications.models import Interview
        
        application = create_test_job_application(user)
        tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
        
        Interview.objects.create(
            application=application,
            interview_type='PHONE',
            date_time=tomorrow,
            location='Phone call'
        )
        
        url = reverse('interview-list')
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
