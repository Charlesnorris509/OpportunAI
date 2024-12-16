# 3. backend/job_tracker/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from applications.views import JobApplicationViewSet
from users.views import UserProfileViewSet

router = DefaultRouter()
router.register(r'applications', JobApplicationViewSet, basename='job-application')
router.register(r'profile', UserProfileViewSet, basename='user-profile')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
