"""
URLs for cover letter app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('templates/', views.cover_letter_templates, name='cover_letter_templates'),
    path('templates/create/', views.create_template, name='create_template'),
    path('templates/edit/<int:template_id>/', views.edit_template, name='edit_template'),
    path('templates/delete/<int:template_id>/', views.delete_template, name='delete_template'),
    path('generate/<int:job_id>/', views.generate_cover_letter_view, name='generate_cover_letter'),
    path('view/<int:job_id>/', views.view_cover_letter, name='view_cover_letter'),
    path('edit/<int:job_id>/', views.edit_cover_letter, name='edit_cover_letter'),
    path('download/<int:job_id>/', views.download_cover_letter, name='download_cover_letter'),
    path('api/generate/', views.api_generate_cover_letter, name='api_generate_cover_letter'),
]
