"""
URLs for automated application app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('schedules/', views.schedules_list, name='schedules_list'),
    path('schedules/create/', views.create_schedule, name='create_schedule'),
    path('schedules/edit/<int:schedule_id>/', views.edit_schedule, name='edit_schedule'),
    path('schedules/delete/<int:schedule_id>/', views.delete_schedule, name='delete_schedule'),
    path('schedules/<int:schedule_id>/', views.schedule_details, name='schedule_details'),
    path('schedules/<int:schedule_id>/run/', views.run_schedule_now, name='run_schedule_now'),
    path('runs/<int:run_id>/', views.run_details, name='run_details'),
    path('dashboard/', views.dashboard, name='automation_dashboard'),
    path('api/schedules/', views.api_get_schedules, name='api_get_schedules'),
    path('api/run-schedule/', views.api_run_schedule, name='api_run_schedule'),
]
