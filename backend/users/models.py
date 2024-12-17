from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    EXPERIENCE_LEVELS = [
        ('ENTRY', 'Entry Level'),
        ('MID', 'Mid Level'),
        ('SENIOR', 'Senior Level'),
        ('EXECUTIVE', 'Executive'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    linkedin_profile = models.URLField(blank=True, null=True)
    experience_level = models.CharField(
        max_length=20, 
        choices=EXPERIENCE_LEVELS, 
        null=True, 
        blank=True
    )
    skills = models.TextField(blank=True)  # Comma-separated skills
    resume_file = models.FileField(upload_to='resumes/', null=True, blank=True)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
