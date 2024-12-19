# models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    preferred_job_title = models.CharField(max_length=100, blank=True)
    years_of_experience = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

class Resume(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()  # Store the resume content
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    file = models.FileField(upload_to='resumes/', null=True, blank=True)
    version = models.IntegerField(default=1)
    generated_for = models.ForeignKey(
        'JobApplication', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='generated_resumes'
    )
    
    class Meta:
        ordering = ['-updated_at']

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return self.name

class UserSkill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    proficiency_level = models.IntegerField(choices=[
        (1, 'Beginner'),
        (2, 'Intermediate'),
        (3, 'Advanced'),
        (4, 'Expert')
    ])
    years_experience = models.FloatField(default=0)
    
    class Meta:
        unique_together = ['user', 'skill']

class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('SAVED', 'Saved'),
        ('APPLIED', 'Applied'),
        ('INTERVIEWING', 'Interviewing'),
        ('OFFERED', 'Offered'),
        ('REJECTED', 'Rejected'),
        ('ACCEPTED', 'Accepted'),
        ('DECLINED', 'Declined')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200)
    job_title = models.CharField(max_length=200)
    job_description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SAVED')
    application_date = models.DateTimeField(null=True, blank=True)
    job_posting_url = models.URLField(blank=True)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    remote_option = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.job_title} at {self.company_name}"

class Interview(models.Model):
    INTERVIEW_TYPE_CHOICES = [
        ('PHONE', 'Phone Screen'),
        ('VIDEO', 'Video Call'),
        ('ONSITE', 'On-site'),
        ('TECHNICAL', 'Technical'),
        ('BEHAVIORAL', 'Behavioral'),
        ('COGNITIVE', 'Cognitive')
    ]
    
    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE)
    interview_type = models.CharField(max_length=20, choices=INTERVIEW_TYPE_CHOICES)
    scheduled_date = models.DateTimeField()
    interviewer_name = models.CharField(max_length=200, blank=True)
    interviewer_title = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=200, blank=True)  # Could be link for virtual interviews
    notes = models.TextField(blank=True)
    feedback = models.TextField(blank=True)
    
    class Meta:
        ordering = ['scheduled_date']

class Document(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('RESUME', 'Resume'),
        ('COVER_LETTER', 'Cover Letter'),
        ('PORTFOLIO', 'Portfolio'),
        ('OTHER', 'Other')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, null=True, blank=True)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='documents/')
    created_at = models.DateTimeField(auto_now_add=True)
    version = models.IntegerField(default=1)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']

class ApplicationLog(models.Model):
    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=100)
    details = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']

class ResumeTemplate(models.Model):
    name = models.CharField(max_length=100)
    content = models.TextField()  # Template content with placeholders
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
