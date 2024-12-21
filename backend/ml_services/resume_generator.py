import openai
from django.conf import settings
from django.core.exceptions import ValidationError
from typing import Optional, Dict, Any
from .models import UserSkill, UserProfile
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ResumeGenerator:
    """Service for generating tailored resumes using OpenAI's GPT models."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the resume generator with optional API key override."""
        self.api_key = api_key or settings.OPENAI_API_KEY
        openai.api_key = self.api_key
        
    def _validate_inputs(self, user_profile: UserProfile, job_description: str) -> None:
        """Validate input parameters before processing."""
        if not job_description or len(job_description.strip()) < 50:
            raise ValidationError("Job description must be at least 50 characters long")
        
        if not user_profile:
            raise ValidationError("User profile is required")
            
    def _format_skills(self, skills: list[UserSkill]) -> str:
        """Format user skills into a readable string."""
        if not skills:
            return "No specific skills listed"
            
        return ", ".join([
            f"{s.skill.name} ({s.proficiency})" 
            for s in skills
        ])
        
    def _create_prompt(self, user_profile: UserProfile, job_description: str, skills_text: str) -> str:
        """Create the prompt for the AI model."""
        return f"""
        Create a professional resume for a job application based on:
        
        Job Description:
        {job_description}
        
        Candidate Skills:
        {skills_text}
        
        Experience: {user_profile.years_of_experience} years
        Current Role: {user_profile.preferred_job_title}
        Education: {user_profile.education if hasattr(user_profile, 'education') else 'Not specified'}
        
        Please format the resume to:
        1. Highlight skills and experience most relevant to the job description
        2. Use bullet points for achievements and responsibilities
        3. Keep it concise and professional
        4. Include a brief professional summary at the top
        """
        
    async def generate_tailored_resume(
        self, 
        user_profile: UserProfile, 
        job_description: str,
        model: str = "gpt-4"
    ) -> Dict[str, Any]:
        """
        Generate a tailored resume based on user profile and job description.
        
        Args:
            user_profile: User's profile containing experience and preferences
            job_description: Target job description
            model: OpenAI model to use (default: gpt-4)
            
        Returns:
            Dict containing generated resume and metadata
            
        Raises:
            ValidationError: If inputs are invalid
            OpenAIError: If API call fails
        """
        try:
            self._validate_inputs(user_profile, job_description)
            
            skills = UserSkill.objects.filter(user=user_profile)
            skills_text = self._format_skills(skills)
            prompt = self._create_prompt(user_profile, job_description, skills_text)
            
            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a professional resume writer focused on creating targeted resumes that highlight relevant skills and experience."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            return {
                'resume': response.choices[0].message.content,
                'model_used': model,
                'timestamp': datetime.now().isoformat(),
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens
            }
            
        except openai.error.OpenAIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error generating resume: {str(e)}")
            raise
