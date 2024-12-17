from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('APPLIED', 'Applied'),
        ('INTERVIEWING', 'Interviewing'),
        ('OFFERED', 'Offered'),
        ('REJECTED', 'Rejected'),
        ('PENDING', 'Pending'),
    ]

    REMOTE_CHOICES = [
        ('FULLY_REMOTE', 'Fully Remote'),
        ('HYBRID', 'Hybrid'),
        ('ON_SITE', 'On-Site'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    company = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100)
    application_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='APPLIED')
    remote_status = models.CharField(max_length=20, choices=REMOTE_CHOICES, null=True, blank=True)
    job_description = models.TextField(blank=True, null=True)
    application_url = models.URLField(blank=True, null=True)
    salary_range = models.CharField(max_length=50, blank=True, null=True)
    
    # Tracking fields
    follow_up_date = models.DateTimeField(null=True, blank=True)
    interview_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.job_title} at {self.company}"

    class Meta:
        ordering = ['-application_date']
        verbose_name_plural = 'Job Applications'
