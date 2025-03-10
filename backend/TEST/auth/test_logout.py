import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db

class TestLogout:
    def test_logout_successful(self, auth_client):
        """Test user can logout successfully."""
        client, user = auth_client
        url = reverse('auth_app:logout')
        
        # First get a refresh token
        login_url = reverse('auth_app:login')
        login_response = client.post(login_url, {
            'username': 'testuser',
            'password': 'password123'
        }, format='json')
        refresh_token = login_response.data['refresh']
        
        # Now logout with that token
        response = client.post(url, {'refresh': refresh_token}, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        
    def test_logout_without_auth(self, api_client):
        """Test logout fails without authentication."""
        url = reverse('auth_app:logout')
        
        response = api_client.post(url, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
