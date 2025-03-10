import pytest
from unittest.mock import patch, MagicMock
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db

class TestResumeGenerator:
    @patch('ml_services.resume_generator.ResumeGenerator.generate_tailored_resume')
    def test_generate_resume(self, mock_generate, auth_client):
        """Test generating a resume."""
        client, user = auth_client
        
        # Mock the return value of the generate_tailored_resume method
        mock_generate.return_value = {
            'resume': 'This is a sample generated resume...',
            'model_used': 'gpt-4',
            'timestamp': '2023-12-01T12:00:00.000Z',
            'prompt_tokens': 500,
            'completion_tokens': 1000,
            'total_tokens': 1500
        }
        
        url = reverse('generate-resume')
        data = {
            'job_description': 'We are looking for a software engineer...',
            'job_title': 'Software Engineer'
        }
        
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'resume' in response.data
        assert 'model_used' in response.data
        
    @patch('ml_services.resume_generator.ResumeGenerator.fetch_sample_resumes')
    def test_fetch_sample_resumes(self, mock_fetch, auth_client):
        """Test fetching sample resumes."""
        client, user = auth_client
        
        # Mock the return value
        mock_fetch.return_value = {
            'sample_resume': 'This is a sample resume template...',
            'model_used': 'gpt-4',
            'timestamp': '2023-12-01T12:00:00.000Z'
        }
        
        url = reverse('sample-resumes')
        response = client.get(url, {'job_title': 'Software Engineer'})
        
        assert response.status_code == status.HTTP_200_OK
        assert 'sample_resume' in response.data
