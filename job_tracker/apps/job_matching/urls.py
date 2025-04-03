"""
URLs for job matching app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('preferences/', views.matching_preferences, name='matching_preferences'),
    path('matches/', views.job_matches, name='job_matches'),
    path('find-matches/', views.find_matches, name='find_matches'),
    path('match/<int:match_id>/', views.match_details, name='match_details'),
    path('match/<int:match_id>/update-status/', views.update_match_status, name='update_match_status'),
    path('auto-apply/', views.auto_apply_dashboard, name='auto_apply_dashboard'),
    path('auto-apply/run/', views.run_auto_apply, name='run_auto_apply'),
    path('recommendations/', views.job_recommendations, name='job_recommendations'),
    path('api/matches/', views.api_get_matches, name='api_get_matches'),
    path('api/find-matches/', views.api_find_matches, name='api_find_matches'),
]
