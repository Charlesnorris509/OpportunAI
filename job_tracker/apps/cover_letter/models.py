"""
Models for cover letter generation and management.
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class CoverLetterTemplate(models.Model):
    """
    Model to store cover letter templates.
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    content = models.TextField(help_text="Template content with placeholders like {{name}}, {{company}}, etc.")
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-is_default', 'name']

class UserCoverLetterTemplate(models.Model):
    """
    Model to store user-specific cover letter templates.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cover_letter_templates')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    content = models.TextField(help_text="Template content with placeholders like {{name}}, {{company}}, etc.")
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"
    
    class Meta:
        ordering = ['-is_default', 'name']
        unique_together = ['user', 'name']

class GeneratedCoverLetter(models.Model):
    """
    Model to store generated cover letters.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_cover_letters')
    job = models.ForeignKey('linkedin_integration.LinkedInJob', on_delete=models.CASCADE, related_name='cover_letters')
    content = models.TextField()
    template_used = models.ForeignKey(CoverLetterTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    user_template_used = models.ForeignKey(UserCoverLetterTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.job.title} at {self.job.company}"
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'job']
