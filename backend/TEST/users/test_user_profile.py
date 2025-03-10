import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db

class TestUserProfile:
    def test_get_profile(self, auth_client):
        """Test retrieving user profile."""
        client, user = auth_client
        url = reverse('user-profile')
        
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user'] == user.id
        
    def test_update_profile(self, auth_client):
        """Test updating user profile."""
        client, user = auth_client
        url = reverse('user-profile')
        
        profile_data = {
            'preferred_job_title': 'Software Developer',
            'location': 'New York',
            'years_of_experience': 5,
            'linkedin_url': 'https://linkedin.com/in/testuser',
            'github_url': 'https://github.com/testuser',
            'phone_number': '+1234567890'
        }
        
        response = client.put(url, profile_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['preferred_job_title'] == profile_data['preferred_job_title']
        assert response.data['location'] == profile_data['location']
