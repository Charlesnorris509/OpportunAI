# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
from django.db.models.signals import pre_save
from django.dispatch import receiver
from pgvector.django import VectorField
import numpy as np
from sentence_transformers import SentenceTransformer

# Initialize the sentence transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)
    preferred_job_title = models.CharField(max_length=100, blank=True)
    years_of_experience = models.IntegerField(default=0)
    profile_embedding = VectorField(dimensions=384, null=True)  # Added vector field
    
    def generate_profile_embedding(self):
        profile_text = f"{self.preferred_job_title} {self.location}"
        return model.encode(profile_text)
    
    def save(self, *args, **kwargs):
        self.profile_embedding = self.generate_profile_embedding()
        super().save(*args, **kwargs)

class Resume(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    content_embedding = VectorField(dimensions=384, null=True)  # Added vector field
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
    
    def generate_content_embedding(self):
        return model.encode(f"{self.title} {self.content}")
    
    def save(self, *args, **kwargs):
        self.content_embedding = self.generate_content_embedding()
        super().save(*args, **kwargs)

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
    job_embedding = VectorField(dimensions=384, null=True)  # Added vector field
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

    def generate_job_embedding(self):
        job_text = f"{self.job_title} {self.company_name} {self.job_description}"
        return model.encode(job_text)
    
    def save(self, *args, **kwargs):
        self.job_embedding = self.generate_job_embedding()
        super().save(*args, **kwargs)

    @staticmethod
    def find_similar_jobs(query_text, limit=5):
        query_embedding = model.encode(query_text)
        return JobApplication.objects.order_by(
            models.F('job_embedding').cosine_distance(query_embedding)
        )[:limit]

# Example usage function for finding matching resumes for a job
def find_matching_resumes(job_application, limit=5):
    return Resume.objects.filter(is_active=True).order_by(
        models.F('content_embedding').cosine_distance(job_application.job_embedding)
    )[:limit]
