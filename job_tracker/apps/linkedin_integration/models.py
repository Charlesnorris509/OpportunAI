"""
Models for LinkedIn integration and job tracking.
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class LinkedInJob(models.Model):
    """
    Model to store LinkedIn job postings.
    """
    job_id = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    requirements = models.TextField(blank=True, null=True)
    responsibilities = models.TextField(blank=True, null=True)
    url = models.URLField()
    posted_date = models.DateField(null=True, blank=True)
    salary_range = models.CharField(max_length=255, blank=True, null=True)
    job_type = models.CharField(max_length=100, blank=True, null=True)
    keywords = models.JSONField(default=list, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} at {self.company}"
    
    class Meta:
        ordering = ['-posted_date', '-created_at']
        indexes = [
            models.Index(fields=['job_id']),
            models.Index(fields=['title']),
            models.Index(fields=['company']),
        ]

class JobApplication(models.Model):
    """
    Model to track job applications submitted by users.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('submitted', 'Submitted'),
        ('interviewing', 'Interviewing'),
        ('rejected', 'Rejected'),
        ('offered', 'Offered'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    job = models.ForeignKey(LinkedInJob, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    cover_letter = models.TextField(blank=True, null=True)
    resume_used = models.FileField(upload_to='resumes/', blank=True, null=True)
    application_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)
    fit_score = models.FloatField(default=0.0, help_text="Score indicating how well the job matches user's resume")
    application_id = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.job.title} at {self.job.company} ({self.status})"
    
    class Meta:
        ordering = ['-application_date']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['status']),
            models.Index(fields=['fit_score']),
        ]
        unique_together = ['user', 'job']

class JobSearchQuery(models.Model):
    """
    Model to store job search queries for recurring searches.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_searches')
    keywords = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    company = models.CharField(max_length=255, blank=True, null=True)
    job_type = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_run = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.keywords}"
    
    class Meta:
        ordering = ['-created_at']
