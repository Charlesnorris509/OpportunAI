# 9. backend/ml_services/resume_generator.py
import openai
import os
from django.conf import settings

class ResumeGenerator:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY

    def generate_tailored_resume(self, job_description, user_profile):
        try:
            prompt = f"""
            Generate a professional resume tailored to the following job description:
            Job Description: {job_description}
            
            Use the following user profile details for personalization:
            User Profile: {user_profile}
            
            Requirements:
            - Highlight matching skills and experiences
            - Use a clean, professional format
            - Emphasize achievements and quantifiable results
            """

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional resume writer."},
                    {"role": "user", "content": prompt}
                ]
            )

            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating resume: {str(e)}"
