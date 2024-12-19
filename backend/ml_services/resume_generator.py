# 9. backend/ml_services/resume_generator.py
import openai
from django.conf import settings
from .models import *
from datetime import datetime, timedelta

class ResumeGenerator:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY

    def generate_tailored_resume(self, user_profile, job_description):
        # Get user's skills and experience
        skills = UserSkill.objects.filter(user=user_profile)
        skill_text = ", ".join([f"{s.skill.name} ({s.proficiency})" for s in skills])
        
        prompt = f"""
        Create a professional resume for a job application based on:
        
        Job Description:
        {job_description}
        
        Candidate Skills:
        {skill_text}
        
        Experience: {user_profile.years_of_experience} years
        Current Role: {user_profile.preferred_job_title}
        
        Format the resume to highlight relevant skills and experience.
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional resume writer."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content
