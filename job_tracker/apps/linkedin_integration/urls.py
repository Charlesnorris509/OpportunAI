"""
URLs for LinkedIn integration app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.job_search, name='job_search'),
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
    path('job/<int:job_id>/apply/', views.apply_for_job, name='apply_for_job'),
    path('applications/', views.application_status, name='application_status'),
    path('auto-apply/', views.auto_apply_jobs, name='auto_apply_jobs'),
]
