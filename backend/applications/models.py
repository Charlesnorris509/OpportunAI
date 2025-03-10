from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from pgvector.django import VectorField
import uuid

class JobApplication(models.Model):
    """Model for tracking job applications"""
    STATUS_CHOICES = [
        ('SAVED', 'Saved'),
        ('APPLIED', 'Applied'),
        ('INTERVIEWING', 'Interviewing'),
        ('OFFERED', 'Offered'),
        ('REJECTED', 'Rejected'),
        ('ACCEPTED', 'Accepted'),
        ('DECLINED', 'Declined')
    ]
    
    REMOTE_CHOICES = [
        ('FULLY_REMOTE', 'Fully Remote'),
        ('HYBRID', 'Hybrid'),
        ('ON_SITE', 'On-Site'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    company_name = models.CharField(max_length=200)
    job_title = models.CharField(max_length=200)
    job_description = models.TextField(blank=True, null=True)
    job_embedding = VectorField(dimensions=384, null=True)  # For semantic search
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SAVED')
    application_date = models.DateTimeField(null=True, blank=True)
    job_posting_url = models.URLField(blank=True, null=True)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    remote_status = models.CharField(max_length=20, choices=REMOTE_CHOICES, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Tracking fields
    follow_up_date = models.DateTimeField(null=True, blank=True)
    interview_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.job_title} at {self.company_name} ({self.status})"
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'job_applications'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['created_at']),
        ]

class Interview(models.Model):
    """Model for tracking interviews"""
    INTERVIEW_TYPES = [
        ('PHONE', 'Phone Screen'),
        ('TECHNICAL', 'Technical Interview'),
        ('BEHAVIORAL', 'Behavioral Interview'),
        ('ONSITE', 'On-site Interview'),
        ('FINAL', 'Final Interview'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name='interviews')
    interview_type = models.CharField(max_length=20, choices=INTERVIEW_TYPES)
    date_time = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True, null=True)  # Could be URL for remote
    interviewer_names = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True)
    feedback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_interview_type_display()} for {self.application.job_title}"
    
    class Meta:
        ordering = ['date_time']
        db_table = 'interviews'

from django.contrib import admin
from .models import *

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'job_title', 'status', 'application_date')
    list_filter = ('status', 'remote_option')
    search_fields = ('company_name', 'job_title')
