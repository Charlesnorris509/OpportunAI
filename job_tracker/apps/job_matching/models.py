"""
Models for job matching and automated application functionality.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class JobMatchingPreference(models.Model):
    """
    Model to store user preferences for job matching and automated applications.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='job_matching_preferences')
    
    # Matching thresholds
    minimum_match_score = models.FloatField(default=0.7, 
                                          help_text="Minimum match score (0.0-1.0) required for job consideration")
    
    # Automated application settings
    enable_auto_apply = models.BooleanField(default=False,
                                          help_text="Enable automated job applications")
    auto_apply_threshold = models.FloatField(default=0.8, 
                                           help_text="Minimum match score (0.0-1.0) required for automated application")
    max_daily_applications = models.IntegerField(default=5,
                                               help_text="Maximum number of automated applications per day")
    
    # Job preferences
    preferred_job_titles = models.JSONField(default=list, blank=True,
                                          help_text="List of preferred job titles")
    preferred_locations = models.JSONField(default=list, blank=True,
                                         help_text="List of preferred job locations")
    preferred_companies = models.JSONField(default=list, blank=True,
                                         help_text="List of preferred companies")
    excluded_companies = models.JSONField(default=list, blank=True,
                                        help_text="List of companies to exclude")
    
    # Notification settings
    notify_on_match = models.BooleanField(default=True,
                                        help_text="Notify when new matching jobs are found")
    notify_on_auto_apply = models.BooleanField(default=True,
                                             help_text="Notify when auto-applying to jobs")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Job Matching Preferences for {self.user.username}"

class JobMatch(models.Model):
    """
    Model to store job matches for users.
    """
    STATUS_CHOICES = [
        ('new', 'New Match'),
        ('viewed', 'Viewed'),
        ('interested', 'Interested'),
        ('not_interested', 'Not Interested'),
        ('applied', 'Applied'),
        ('auto_applied', 'Auto Applied'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_matches')
    job = models.ForeignKey('linkedin_integration.LinkedInJob', on_delete=models.CASCADE, related_name='matches')
    match_score = models.FloatField(help_text="Match score between 0.0 and 1.0")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    
    # Match details
    matching_skills = models.JSONField(default=list, blank=True)
    missing_skills = models.JSONField(default=list, blank=True)
    
    # Auto-apply details
    auto_apply_eligible = models.BooleanField(default=False)
    auto_apply_attempted = models.BooleanField(default=False)
    auto_apply_result = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.job.title} at {self.job.company} ({self.match_score:.2f})"
    
    class Meta:
        ordering = ['-match_score', '-created_at']
        unique_together = ['user', 'job']

class AutomatedApplicationLog(models.Model):
    """
    Model to log automated job applications.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='automated_applications')
    job = models.ForeignKey('linkedin_integration.LinkedInJob', on_delete=models.CASCADE, related_name='automated_applications')
    job_match = models.ForeignKey(JobMatch, on_delete=models.CASCADE, related_name='application_logs')
    application = models.ForeignKey('linkedin_integration.JobApplication', on_delete=models.SET_NULL, 
                                   related_name='automation_log', null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    match_score = models.FloatField()
    cover_letter = models.TextField()
    
    attempt_date = models.DateTimeField(default=timezone.now)
    completion_date = models.DateTimeField(null=True, blank=True)
    
    error_message = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Auto Application: {self.user.username} - {self.job.title} at {self.job.company} ({self.status})"
    
    class Meta:
        ordering = ['-attempt_date']
