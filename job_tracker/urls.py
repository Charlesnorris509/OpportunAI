"""
Main project URLs configuration.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('linkedin/', include('job_tracker.apps.linkedin_integration.urls')),
    path('resume/', include('job_tracker.apps.resume_analysis.urls')),
    path('cover-letter/', include('job_tracker.apps.cover_letter.urls')),
    path('job-matching/', include('job_tracker.apps.job_matching.urls')),
    path('automation/', include('job_tracker.apps.automated_application.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
