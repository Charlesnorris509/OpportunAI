import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db

class TestLogin:
    def test_login_successful(self, api_client, create_user):
        """Test user can login with valid credentials."""
        user = create_user()
        url = reverse('auth_app:login')
        
        response = api_client.post(url, {
            'username': 'testuser',
            'password': 'password123'
        }, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        
    def test_login_invalid_credentials(self, api_client):
        """Test login fails with invalid credentials."""
        url = reverse('auth_app:login')
        
        response = api_client.post(url, {
            'username': 'wronguser',
            'password': 'wrongpass'
        }, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
