"""
URLs for resume analysis app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('analyze/', views.analyze_resume, name='analyze_resume'),
    path('job-match/<int:job_id>/', views.job_match_analysis, name='job_match_analysis'),
    path('batch-analyze/', views.batch_analyze_jobs, name='batch_analyze_jobs'),
    path('api/calculate-fit-score/', views.api_calculate_fit_score, name='api_calculate_fit_score'),
]
