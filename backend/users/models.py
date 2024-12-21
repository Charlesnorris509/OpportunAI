from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import URLValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from datetime import date
import os

class UserProfile(models.Model):
    """
    Extended user profile model with professional information and resume details.
    """
    
    class ExperienceLevel(models.TextChoices):
        ENTRY = 'ENTRY', 'Entry Level (0-2 years)'
        MID = 'MID', 'Mid Level (3-5 years)'
        SENIOR = 'SENIOR', 'Senior Level (6-10 years)'
        LEAD = 'LEAD', 'Team Lead (8+ years)'
        EXECUTIVE = 'EXECUTIVE', 'Executive (10+ years)'

    class EmploymentStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Actively Looking'
        PASSIVE = 'PASSIVE', 'Open to Opportunities'
        EMPLOYED = 'EMPLOYED', 'Not Looking'
        
    # Core Fields
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='profile'
    )
    
    # Professional Details
    preferred_job_title = models.CharField(
        max_length=100,
        help_text="Your desired job title",
        blank=True
    )
    years_of_experience = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True,
        help_text="Total years of professional experience"
    )
    experience_level = models.CharField(
        max_length=20,
        choices=ExperienceLevel.choices,
        default=ExperienceLevel.ENTRY
    )
    employment_status = models.CharField(
        max_length=20,
        choices=EmploymentStatus.choices,
        default=EmploymentStatus.ACTIVE
    )
    
    # Bio and Social
    bio = models.TextField(
        blank=True,
        help_text="Brief professional summary"
    )
    linkedin_profile = models.URLField(
        blank=True,
        validators=[URLValidator(schemes=['https'])],
        help_text="Your LinkedIn profile URL"
    )
    github_profile = models.URLField(
        blank=True,
        validators=[URLValidator(schemes=['https'])],
        help_text="Your GitHub profile URL"
    )
    portfolio_website = models.URLField(
        blank=True,
        validators=[URLValidator(schemes=['https', 'http'])],
        help_text="Your portfolio website URL"
    )
    
    # Location and Availability
    location = models.CharField(
        max_length=100,
        blank=True,
        help_text="City, State/Province, Country"
    )
    willing_to_relocate = models.BooleanField(
        default=False,
        help_text="Are you willing to relocate for work?"
    )
    remote_work_preference = models.CharField(
        max_length=20,
        choices=[
            ('ONSITE', 'On-site only'),
            ('HYBRID', 'Hybrid preferred'),
            ('REMOTE', 'Remote only'),
            ('FLEXIBLE', 'Flexible')
        ],
        default='FLEXIBLE'
    )
    
    # Resume and Documents
    resume_file = models.FileField(
        upload_to='resumes/%Y/%m/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])],
        blank=True,
        help_text="Upload your latest resume (PDF, DOC, or DOCX)"
    )
    last_resume_update = models.DateTimeField(
        auto_now=True,
        help_text="Last time resume was updated"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['experience_level', 'employment_status']),
            models.Index(fields=['user', 'created_at'])
        ]
        
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}'s Profile"
    
    def clean(self):
        """Validate model data."""
        if self.linkedin_profile and not self.linkedin_profile.startswith('https://www.linkedin.com/'):
            raise ValidationError({
                'linkedin_profile': 'Please enter a valid LinkedIn profile URL'
            })
            
        if self.github_profile and not self.github_profile.startswith('https://github.com/'):
            raise ValidationError({
                'github_profile': 'Please enter a valid GitHub profile URL'
            })
    
    def get_resume_filename(self):
        """Get the filename of the uploaded resume."""
        return os.path.basename(self.resume_file.name) if self.resume_file else None
    
    def get_experience_range(self):
        """Get the experience range based on experience level."""
        ranges = {
            'ENTRY': '0-2 years',
            'MID': '3-5 years',
            'SENIOR': '6-10 years',
            'LEAD': '8+ years',
            'EXECUTIVE': '10+ years'
        }
        return ranges.get(self.experience_level, 'Not specified')
    
    @property
    def is_profile_complete(self):
        """Check if the user profile is complete with essential information."""
        required_fields = [
            self.preferred_job_title,
            self.bio,
            self.years_of_experience,
            self.location,
            self.resume_file
        ]
        return all(bool(field) for field in required_fields)

# Signal handlers
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile instance when a new User is created."""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile instance when the User is saved."""
    if not hasattr(instance, 'profile'):
        UserProfile.objects.create(user=instance)
    instance.profile.save()
