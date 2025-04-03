"""
Models for resume analysis and keyword extraction.
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ResumeKeywords(models.Model):
    """
    Model to store extracted keywords from user resumes.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='resume_keywords')
    skills = models.JSONField(default=list)
    experience = models.JSONField(default=list)
    education = models.JSONField(default=list)
    certifications = models.JSONField(default=list)
    languages = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Resume Keywords for {self.user.username}"
    
    class Meta:
        verbose_name_plural = "Resume Keywords"

class JobKeywords(models.Model):
    """
    Model to store extracted keywords from job descriptions.
    """
    job = models.OneToOneField('linkedin_integration.LinkedInJob', on_delete=models.CASCADE, related_name='keywords_analysis')
    required_skills = models.JSONField(default=list)
    preferred_skills = models.JSONField(default=list)
    experience_requirements = models.JSONField(default=list)
    education_requirements = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Job Keywords for {self.job.title} at {self.job.company}"
    
    class Meta:
        verbose_name_plural = "Job Keywords"
