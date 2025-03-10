import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status

pytestmark = pytest.mark.django_db

class TestRegister:
    def test_register_successful(self, api_client):
        """Test user registration with valid data."""
        url = reverse('auth_app:register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'StrongPassword123!',
            'password_confirm': 'StrongPassword123!'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username='newuser').exists()
        assert 'access' in response.data
        assert 'refresh' in response.data
        
    def test_register_password_mismatch(self, api_client):
        """Test registration fails when passwords don't match."""
        url = reverse('auth_app:register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'StrongPassword123!',
            'password_confirm': 'DifferentPassword123!'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not User.objects.filter(username='newuser').exists()
        
    def test_register_duplicate_email(self, api_client, create_user):
        """Test registration fails with duplicate email."""
        existing_user = create_user(email="existing@example.com")
        
        url = reverse('auth_app:register')
        data = {
            'username': 'newuser',
            'email': 'existing@example.com',
            'password': 'StrongPassword123!',
            'password_confirm': 'StrongPassword123!'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
