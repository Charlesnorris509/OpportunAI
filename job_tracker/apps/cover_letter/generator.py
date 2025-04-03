"""
Cover letter generation utilities.
"""
import os
import re
import logging
from typing import Dict, List, Optional, Any
import json
import string
from datetime import datetime

from ..resume_analysis.utils import extract_text_from_resume, extract_keywords_from_text, extract_job_requirements

logger = logging.getLogger(__name__)

# Default cover letter templates
DEFAULT_TEMPLATES = [
    {
        "name": "Standard Professional",
        "description": "A professional and straightforward cover letter template suitable for most industries.",
        "content": """
[Your Name]
[Your Address]
[City, State ZIP]
[Your Email]
[Your Phone]
[Date]

[Hiring Manager's Name]
[Company Name]
[Company Address]
[City, State ZIP]

Dear {{hiring_manager_name or "Hiring Manager"}},

I am writing to express my interest in the {{job_title}} position at {{company_name}} that I found on LinkedIn. With my background in {{relevant_background}} and experience with {{relevant_skills}}, I believe I am well-qualified for this role.

{{job_specific_paragraph}}

Throughout my career, I have {{career_highlights}}. My experience with {{matching_skills}} aligns perfectly with the requirements outlined in your job description. I am particularly drawn to {{company_name}} because {{company_interest}}.

I am excited about the opportunity to bring my unique skills to {{company_name}} and help {{job_contribution}}. I am confident that my background and passion for {{industry_or_field}} make me an ideal candidate for this position.

Thank you for considering my application. I look forward to the opportunity to discuss how my experience and skills would benefit {{company_name}}.

Sincerely,

{{your_name}}
"""
    },
    {
        "name": "Technical Professional",
        "description": "A cover letter template focused on technical skills and achievements, ideal for IT and engineering roles.",
        "content": """
[Your Name]
[Your Address]
[City, State ZIP]
[Your Email]
[Your Phone]
[Date]

[Hiring Manager's Name]
[Company Name]
[Company Address]
[City, State ZIP]

Dear {{hiring_manager_name or "Hiring Manager"}},

I am excited to apply for the {{job_title}} position at {{company_name}} as advertised on LinkedIn. As a professional with {{years_of_experience}} years of experience in {{technical_field}}, I offer a strong combination of technical expertise and {{additional_strength}} that I believe would make me a valuable addition to your team.

My technical skills include {{technical_skills_list}}, which directly align with the requirements in your job description. In my current role at {{current_or_previous_company}}, I {{technical_achievement}} which resulted in {{achievement_result}}. This experience has prepared me well for the challenges of the {{job_title}} role at {{company_name}}.

I am particularly impressed by {{company_name}}'s {{company_achievement_or_product}} and would be thrilled to contribute to your ongoing success in {{industry_or_field}}. Your company's commitment to {{company_value}} resonates with my professional values and goals.

I welcome the opportunity to discuss how my technical background, combined with my {{soft_skill}}, can help {{company_name}} achieve its objectives. Thank you for considering my application.

Sincerely,

{{your_name}}
"""
    },
    {
        "name": "Creative Professional",
        "description": "A more creative and personable cover letter template suitable for marketing, design, and creative industries.",
        "content": """
[Your Name]
[Your Address]
[City, State ZIP]
[Your Email]
[Your Phone]
[Date]

[Hiring Manager's Name]
[Company Name]
[Company Address]
[City, State ZIP]

Dear {{hiring_manager_name or "Hiring Manager"}},

When I discovered the {{job_title}} position at {{company_name}}, I was immediately excited by the opportunity to bring my creative approach to {{creative_field}} to your innovative team.

My journey in {{creative_field}} has equipped me with a unique perspective and a diverse skill set including {{creative_skills}}. At {{current_or_previous_company}}, I had the opportunity to {{creative_achievement}}, which {{achievement_impact}}. This experience, combined with my expertise in {{technical_tools}}, has prepared me to make meaningful contributions to {{company_name}}'s creative initiatives.

What draws me to {{company_name}} is your commitment to {{company_creative_approach}}. I admire how your team has {{company_achievement}}, and I'm excited by the prospect of contributing to future projects that continue to {{industry_impact}}.

I believe that creativity thrives in collaborative environments where diverse perspectives are valued. My ability to {{collaborative_skill}} would complement your team's existing strengths and help drive innovation in {{specific_area}}.

I would love the opportunity to discuss how my creative vision and technical skills could benefit {{company_name}}. Thank you for considering my application.

With creative enthusiasm,

{{your_name}}
"""
    }
]

def load_default_templates():
    """
    Load default cover letter templates.
    """
    return DEFAULT_TEMPLATES

def extract_resume_info(resume_path: str) -> Dict[str, Any]:
    """
    Extract relevant information from a resume for cover letter generation.
    
    Args:
        resume_path: Path to the resume file
        
    Returns:
        Dictionary containing extracted resume information
    """
    try:
        # Extract text from resume
        resume_text = extract_text_from_resume(resume_path)
        if not resume_text:
            logger.error(f"Failed to extract text from resume: {resume_path}")
            return {}
        
        # Extract keywords from resume
        keywords = extract_keywords_from_text(resume_text)
        
        # Extract name (assuming it's at the beginning of the resume)
        name_match = re.search(r'^([A-Z][a-z]+(?: [A-Z][a-z]+)+)', resume_text)
        name = name_match.group(1) if name_match else "Your Name"
        
        # Extract contact information
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text)
        email = email_match.group(0) if email_match else "your.email@example.com"
        
        phone_match = re.search(r'\b(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b', resume_text)
        phone = phone_match.group(0) if phone_match else "123-456-7890"
        
        # Extract experience
        experience_years = 0
        for exp in keywords['experience']:
            year_match = re.search(r'(\d+)', exp)
            if year_match:
                experience_years = max(experience_years, int(year_match.group(1)))
        
        # Extract most recent job title and company
        job_title = "Professional"
        company = "Previous Company"
        
        # Try to extract job title and company from resume
        job_title_patterns = [
            r'(?:^|\n)([A-Z][a-z]+(?: [A-Z][a-z]+)*)\s+(?:at|,)\s+([A-Z][a-z]+(?: [A-Z][a-z]+)*)',
            r'(?:^|\n)([A-Z][a-z]+(?: [A-Z][a-z]+)*)\n([A-Z][a-z]+(?: [A-Z][a-z]+)*)'
        ]
        
        for pattern in job_title_patterns:
            matches = re.findall(pattern, resume_text)
            if matches:
                job_title = matches[0][0]
                company = matches[0][1]
                break
        
        return {
            'name': name,
            'email': email,
            'phone': phone,
            'skills': keywords['skills'],
            'experience_years': experience_years,
            'job_title': job_title,
            'company': company,
            'education': keywords['education'],
            'languages': keywords['languages']
        }
        
    except Exception as e:
        logger.exception(f"Error extracting resume info: {str(e)}")
        return {}

def generate_cover_letter(resume_path: str, job_description: str, 
                         applicant_name: str, job_title: str, 
                         company_name: str, template_id: Optional[int] = None) -> str:
    """
    Generate a tailored cover letter based on resume and job description.
    
    Args:
        resume_path: Path to the resume file
        job_description: Job description text
        applicant_name: Name of the applicant
        job_title: Job title
        company_name: Company name
        template_id: Optional template ID to use
        
    Returns:
        Generated cover letter text
    """
    try:
        # Extract resume information
        resume_info = extract_resume_info(resume_path)
        
        # Extract job requirements
        job_requirements = extract_job_requirements(job_description)
        
        # Get matching skills
        matching_skills = []
        if resume_info.get('skills') and job_requirements.get('required_skills'):
            matching_skills = list(set(resume_info['skills']).intersection(set(job_requirements['required_skills'])))
        
        # Get template content
        template_content = DEFAULT_TEMPLATES[0]['content']  # Default to first template
        if template_id is not None and 0 <= template_id < len(DEFAULT_TEMPLATES):
            template_content = DEFAULT_TEMPLATES[template_id]['content']
        
        # Prepare template variables
        today = datetime.now().strftime("%B %d, %Y")
        
        # Format skills lists
        technical_skills = ", ".join(resume_info.get('skills', [])[:5])
        matching_skills_text = ", ".join(matching_skills[:3])
        
        # Create job-specific paragraph based on matching skills
        if matching_skills:
            job_specific_paragraph = f"I noticed that you are looking for candidates with experience in {matching_skills_text}. In my previous role at {resume_info.get('company', 'my previous company')}, I utilized these skills to deliver successful projects and contribute to team objectives."
        else:
            job_specific_paragraph = f"After reviewing the job description, I am confident that my skills and experiences make me a strong candidate for this position. I am particularly interested in applying my knowledge of {technical_skills} to the challenges and opportunities at {company_name}."
        
        # Determine relevant background based on job title
        relevant_background = ""
        if "developer" in job_title.lower() or "engineer" in job_title.lower():
            relevant_background = "software development"
        elif "data" in job_title.lower() or "analyst" in job_title.lower():
            relevant_background = "data analysis"
        elif "manager" in job_title.lower() or "director" in job_title.lower():
            relevant_background = "team leadership"
        elif "designer" in job_title.lower():
            relevant_background = "design"
        elif "marketing" in job_title.lower():
            relevant_background = "marketing"
        else:
            relevant_background = resume_info.get('job_title', 'professional work')
        
        # Career highlights based on experience years
        experience_years = resume_info.get('experience_years', 0)
        if experience_years > 5:
            career_highlights = f"developed a strong track record of success over {experience_years} years in the industry"
        elif experience_years > 0:
            career_highlights = f"built valuable skills and knowledge during my {experience_years} years of experience"
        else:
            career_highlights = "developed a strong foundation of relevant skills and knowledge"
        
        # Company interest
        company_interest = f"of your reputation for innovation and excellence in the industry"
        
        # Job contribution
        job_contribution = "contribute to your ongoing success"
        
        # Replace template variables
        template_vars = {
            'your_name': applicant_name,
            'hiring_manager_name': "",  # Default to empty, will use fallback in template
            'job_title': job_title,
            'company_name': company_name,
            'relevant_background': relevant_background,
            'relevant_skills': technical_skills,
            'job_specific_paragraph': job_specific_paragraph,
            'career_highlights': career_highlights,
            'matching_skills': matching_skills_text if matching_skills else technical_skills,
            'company_interest': company_interest,
            'job_contribution': job_contribution,
            'industry_or_field': relevant_background,
            'date': today,
            'years_of_experience': str(experience_years) if experience_years > 0 else "several",
            'technical_field': relevant_background,
            'additional_strength': "problem-solving abilities",
            'technical_skills_list': technical_skills,
            'current_or_previous_company': resume_info.get('company', 'my previous company'),
            'technical_achievement': "successfully implemented key projects",
            'achievement_result': "improved efficiency and productivity",
            'company_achievement_or_product': "innovative approach to " + relevant_background,
            'company_value': "excellence and innovation",
            'soft_skill': "communication skills and teamwork",
            'creative_field': relevant_background,
            'creative_skills': technical_skills,
            'creative_achievement': "led creative initiatives",
            'achievement_impact': "resulted in positive outcomes",
            'technical_tools': technical_skills,
            'company_creative_approach': "creativity and innovation",
            'company_achievement': "achieved impressive results",
            'industry_impact': "make a positive impact",
            'collaborative_skill': "collaborate effectively with diverse teams",
            'specific_area': relevant_background
        }
        
        # Replace template variables
        cover_letter = string.Template(template_content).safe_substitute(template_vars)
        
        # Clean up any remaining template variables
        cover_letter = re.sub(r'{{.*?}}', '', cover_letter)
        
        return cover_letter
        
    except Exception as e:
        logger.exception(f"Error generating cover letter: {str(e)}")
        return f"Error generating cover letter: {str(e)}"
