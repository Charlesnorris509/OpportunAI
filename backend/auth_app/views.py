from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.conf import settings
from .serializers import (
    RegisterSerializer, LoginSerializer, 
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer
)
from datetime import datetime, timedelta
from .models import UserToken
import logging

logger = logging.getLogger(__name__)

class RegisterView(generics.CreateAPIView):
    """User registration endpoint"""
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create tokens
        refresh = RefreshToken.for_user(user)
        
        # Log new user registration
        logger.info(f"New user registered: {user.username}")
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        }, status=status.HTTP_201_CREATED)

class LoginView(generics.GenericAPIView):
    """User login endpoint"""
    permission_classes = (permissions.AllowAny,)
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # Create tokens
        refresh = RefreshToken.for_user(user)
        
        # Store refresh token in database
        expires = datetime.now() + timedelta(days=settings.SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME').days)
        UserToken.objects.create(
            user=user,
            refresh_token=str(refresh),
            expires_at=expires
        )
        
        # Log successful login
        logger.info(f"User login successful: {user.username}")
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            }
        })

class LogoutView(APIView):
    """User logout endpoint"""
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                # Revoke token in database
                token = UserToken.objects.filter(
                    user=request.user, 
                    refresh_token=refresh_token,
                    is_active=True
                ).first()
                
                if token:
                    token.revoke()
            
            logger.info(f"User logged out: {request.user.username}")
            return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Logout error for user {request.user.username}: {str(e)}")
            return Response({"detail": "Error logging out"}, status=status.HTTP_400_BAD_REQUEST)
