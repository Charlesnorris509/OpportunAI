"""
Models for automated application system.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class AutomatedApplicationSchedule(models.Model):
    """
    Model to store automated application schedules.
    """
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('custom', 'Custom'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='application_schedules')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Schedule settings
    is_active = models.BooleanField(default=True)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='daily')
    days_of_week = models.JSONField(default=list, blank=True, 
                                  help_text="List of days (0-6, where 0 is Monday) for weekly schedules")
    time_of_day = models.TimeField(default=timezone.now)
    
    # Search criteria
    keywords = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    job_type = models.CharField(max_length=100, blank=True, null=True)
    
    # Application limits
    max_applications_per_run = models.IntegerField(default=5)
    min_match_score = models.FloatField(default=0.8)
    
    # Tracking
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    total_applications = models.IntegerField(default=0)
    successful_applications = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"
    
    class Meta:
        ordering = ['-created_at']

class AutomatedApplicationRun(models.Model):
    """
    Model to store automated application run results.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    schedule = models.ForeignKey(AutomatedApplicationSchedule, on_delete=models.CASCADE, related_name='runs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    
    jobs_found = models.IntegerField(default=0)
    applications_attempted = models.IntegerField(default=0)
    applications_successful = models.IntegerField(default=0)
    
    error_message = models.TextField(blank=True, null=True)
    log = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.schedule.name} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"
    
    class Meta:
        ordering = ['-start_time']

class AutomatedApplicationRunJob(models.Model):
    """
    Model to store jobs processed in an automated application run.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('applied', 'Applied'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
    ]
    
    run = models.ForeignKey(AutomatedApplicationRun, on_delete=models.CASCADE, related_name='jobs')
    job = models.ForeignKey('linkedin_integration.LinkedInJob', on_delete=models.CASCADE, related_name='automated_run_jobs')
    job_match = models.ForeignKey('job_matching.JobMatch', on_delete=models.SET_NULL, related_name='automated_run_jobs', null=True, blank=True)
    application = models.ForeignKey('linkedin_integration.JobApplication', on_delete=models.SET_NULL, related_name='automated_run_job', null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    match_score = models.FloatField()
    
    processed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.job.title} at {self.job.company} - {self.status}"
    
    class Meta:
        ordering = ['-match_score']
