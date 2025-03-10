import openai
from django.conf import settings
from django.core.exceptions import ValidationError
from typing import Optional, Dict, Any
from .models import UserSkill, UserProfile
from datetime import datetime
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
        if not user_profile:
            raise ValidationError("User profile is required.")
        
        if not job_description or len(job_description.strip()) < 50:
            raise ValidationError("Job description must be at least 50 characters long.")
        
        if not UserSkill.objects.filter(user=user_profile).exists():
            raise ValidationError("User profile must have at least one skill.")
        
        if not user_profile.email or "@" not in user_profile.email:
            raise ValidationError("A valid email address is required.")
        
        if not user_profile.full_name:
            raise ValidationError("Full name is required.")
        
    def _format_skills(self, skills: list[UserSkill]) -> str:
        """Format user skills into a readable string."""
        return ", ".join(f"{skill.skill.name} ({skill.proficiency})" for skill in skills) or "No specific skills listed."
    
    def _create_prompt(self, user_profile: UserProfile, job_description: str, skills_text: str) -> str:
        """Create the prompt for the AI model."""
        achievements = getattr(user_profile, 'achievements', 'Not specified')
        education = getattr(user_profile, 'education', 'Not specified')
        
        return f"""
        Create a professional resume tailored for the following job:

        Job Description:
        {job_description.strip()}
        
        Candidate Skills:
        {skills_text}
        
        Experience: {user_profile.years_of_experience} years
        Current Role: {user_profile.preferred_job_title}
        Education: {education}
        Achievements: {achievements}
        Email: {user_profile.email}
        Full Name: {user_profile.full_name}
        
        Requirements:
        1. Highlight skills and experiences most relevant to the job description.
        2. Use bullet points for achievements and responsibilities.
        3. Keep it concise and professional.
        4. Include a brief professional summary at the top.
        5. Emphasize quantifiable outcomes wherever possible.
        """
    
    def _log_request(self, prompt: str, user_profile: UserProfile) -> None:
        """Log request details for debugging and auditing."""
        logger.info(f"Generating resume for user {user_profile.id} with prompt length: {len(prompt)}")
    
    async def generate_tailored_resume(
        self,
        user_profile: UserProfile,
        job_description: str,
        model: str = "gpt-4"
    ) -> Dict[str, Any]:
        """
        Generate a tailored resume based on user profile and job description.

        Args:
            user_profile (UserProfile): User's profile containing experience and preferences.
            job_description (str): Target job description.
            model (str): OpenAI model to use (default: gpt-4).

        Returns:
            dict: A dictionary containing generated resume, metadata, and token usage.
        """
        try:
            # Input validation
            self._validate_inputs(user_profile, job_description)
            
            # Fetch user skills
            skills = await UserSkill.objects.filter(user=user_profile).all()
            skills_text = self._format_skills(skills)
            
            # Create prompt
            prompt = self._create_prompt(user_profile, job_description, skills_text)
            self._log_request(prompt, user_profile)
            
            # Generate response from OpenAI
            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional resume writer focused on creating tailored resumes that highlight relevant skills and experiences."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000,
            )
            
            # Process response
            content = response.choices[0].message.content
            metadata = {
                'model_used': model,
                'timestamp': datetime.now().isoformat(),
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            }
            
            logger.info(f"Resume generated successfully for user {user_profile.id}. Total tokens used: {metadata['total_tokens']}")
            return {'resume': content, **metadata}
        
        except ValidationError as ve:
            logger.warning(f"Validation error: {ve}")
            raise ve
        except openai.error.OpenAIError as oe:
            logger.error(f"OpenAI API error: {oe}")
            raise oe
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise

    async def fetch_sample_resumes(self, job_title: str, model: str = "gpt-4") -> Dict[str, Any]:
        """
        Generate a sample resume template based on the job title.

        Args:
            job_title (str): The job title for which the resume is to be generated.
            model (str): OpenAI model to use (default: gpt-4).

        Returns:
            dict: A dictionary containing a sample resume and metadata.
        """
        try:
            prompt = f"Generate a generic but professional resume template for a {job_title}."
            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a professional resume writer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            return {
                'sample_resume': response.choices[0].message.content,
                'model_used': model,
                'timestamp': datetime.now().isoformat(),
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens
            }
        except openai.error.OpenAIError as oe:
            logger.error(f"OpenAI API error while fetching sample resumes: {oe}")
            raise
