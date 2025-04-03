"""
Utility functions for resume analysis and keyword matching.
"""
import os
import re
import logging
import PyPDF2
import docx
from collections import Counter
from typing import Dict, List, Tuple, Set, Optional, Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)

# Common skills and keywords for different job categories
COMMON_TECH_SKILLS = {
    'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin', 'go', 'rust', 'typescript'],
    'web': ['html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 'spring', 'asp.net'],
    'database': ['sql', 'mysql', 'postgresql', 'mongodb', 'oracle', 'redis', 'elasticsearch', 'dynamodb', 'cassandra'],
    'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'serverless', 'lambda', 'ec2', 's3'],
    'data': ['pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch', 'hadoop', 'spark', 'tableau', 'power bi']
}

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text content
    """
    try:
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
        return text
    except Exception as e:
        logger.exception(f"Error extracting text from PDF: {str(e)}")
        return ""

def extract_text_from_docx(docx_path: str) -> str:
    """
    Extract text content from a DOCX file.
    
    Args:
        docx_path: Path to the DOCX file
        
    Returns:
        Extracted text content
    """
    try:
        doc = docx.Document(docx_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        logger.exception(f"Error extracting text from DOCX: {str(e)}")
        return ""

def extract_text_from_resume(resume_path: str) -> str:
    """
    Extract text content from a resume file (PDF or DOCX).
    
    Args:
        resume_path: Path to the resume file
        
    Returns:
        Extracted text content
    """
    file_ext = os.path.splitext(resume_path)[1].lower()
    
    if file_ext == '.pdf':
        return extract_text_from_pdf(resume_path)
    elif file_ext == '.docx':
        return extract_text_from_docx(resume_path)
    else:
        logger.error(f"Unsupported file format: {file_ext}")
        return ""

def extract_keywords_from_text(text: str) -> Dict[str, List[str]]:
    """
    Extract keywords from text content.
    
    Args:
        text: Text content to extract keywords from
        
    Returns:
        Dictionary of extracted keywords by category
    """
    text = text.lower()
    
    # Extract skills
    skills = []
    for category, skill_list in COMMON_TECH_SKILLS.items():
        for skill in skill_list:
            # Match whole words only
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text):
                skills.append(skill)
    
    # Extract education
    education = []
    education_patterns = [
        r'\b(bachelor|master|phd|doctorate|bs|ba|ms|ma|mba)\b',
        r'\b(degree|diploma|certificate)\b',
        r'\buniversity\s+of\s+\w+\b',
        r'\b\w+\s+university\b',
        r'\b\w+\s+college\b'
    ]
    
    for pattern in education_patterns:
        matches = re.findall(pattern, text)
        education.extend(matches)
    
    # Extract experience
    experience = []
    experience_patterns = [
        r'\b(\d+)\s+(year|yr)s?\b',
        r'\b(senior|junior|lead|principal|staff)\b',
        r'\b(manager|director|vp|chief|head)\b'
    ]
    
    for pattern in experience_patterns:
        matches = re.findall(pattern, text)
        if isinstance(matches[0], tuple) if matches else False:
            experience.extend([' '.join(match) for match in matches])
        else:
            experience.extend(matches)
    
    # Extract languages
    languages = []
    language_patterns = [
        r'\b(english|spanish|french|german|chinese|japanese|russian|arabic|portuguese|italian)\b'
    ]
    
    for pattern in language_patterns:
        matches = re.findall(pattern, text)
        languages.extend(matches)
    
    return {
        'skills': list(set(skills)),
        'education': list(set(education)),
        'experience': list(set(experience)),
        'languages': list(set(languages))
    }

def extract_job_requirements(job_description: str) -> Dict[str, List[str]]:
    """
    Extract required and preferred skills from a job description.
    
    Args:
        job_description: Job description text
        
    Returns:
        Dictionary of required and preferred skills
    """
    job_description = job_description.lower()
    
    # Extract required skills
    required_skills = []
    required_sections = [
        r'required skills',
        r'requirements',
        r'qualifications',
        r'what you need',
        r'must have',
        r'essential'
    ]
    
    # Extract preferred skills
    preferred_skills = []
    preferred_sections = [
        r'preferred skills',
        r'nice to have',
        r'desirable',
        r'bonus points',
        r'plus'
    ]
    
    # Find all skills in the job description
    all_skills = []
    for category, skill_list in COMMON_TECH_SKILLS.items():
        for skill in skill_list:
            # Match whole words only
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, job_description):
                all_skills.append(skill)
    
    # Categorize skills as required or preferred
    for skill in all_skills:
        # Check if skill is in a required section
        is_required = False
        for section in required_sections:
            if re.search(section, job_description):
                section_pos = re.search(section, job_description).start()
                next_section_pos = float('inf')
                
                # Find the next section after this one
                for other_section in required_sections + preferred_sections:
                    if other_section != section:
                        match = re.search(other_section, job_description[section_pos+len(section):])
                        if match:
                            next_section_pos = min(next_section_pos, section_pos + len(section) + match.start())
                
                # Check if skill is in this section
                section_text = job_description[section_pos:next_section_pos]
                pattern = r'\b' + re.escape(skill) + r'\b'
                if re.search(pattern, section_text):
                    required_skills.append(skill)
                    is_required = True
                    break
        
        # If not required, check if it's preferred
        if not is_required:
            for section in preferred_sections:
                if re.search(section, job_description):
                    section_pos = re.search(section, job_description).start()
                    next_section_pos = float('inf')
                    
                    # Find the next section after this one
                    for other_section in required_sections + preferred_sections:
                        if other_section != section:
                            match = re.search(other_section, job_description[section_pos+len(section):])
                            if match:
                                next_section_pos = min(next_section_pos, section_pos + len(section) + match.start())
                    
                    # Check if skill is in this section
                    section_text = job_description[section_pos:next_section_pos]
                    pattern = r'\b' + re.escape(skill) + r'\b'
                    if re.search(pattern, section_text):
                        preferred_skills.append(skill)
                        break
    
    # If no skills were categorized, assume all skills are required
    if not required_skills and not preferred_skills:
        required_skills = all_skills
    
    # Extract experience requirements
    experience_requirements = []
    experience_patterns = [
        r'(\d+)[\+]?\s+(year|yr)s?(\s+of\s+experience)?',
        r'experience\s+of\s+(\d+)[\+]?\s+(year|yr)s?',
        r'(\d+)[\+]?\s+(year|yr)s?(\s+experience)?'
    ]
    
    for pattern in experience_patterns:
        matches = re.findall(pattern, job_description)
        if matches:
            for match in matches:
                if isinstance(match, tuple):
                    experience_requirements.append(f"{match[0]}+ years")
                else:
                    experience_requirements.append(match)
    
    # Extract education requirements
    education_requirements = []
    education_patterns = [
        r'(bachelor|master|phd|doctorate|bs|ba|ms|ma|mba)(\s+degree)?',
        r'degree\s+in\s+(\w+(\s+\w+)*)',
        r'(computer science|engineering|information technology|data science)'
    ]
    
    for pattern in education_patterns:
        matches = re.findall(pattern, job_description)
        if matches:
            for match in matches:
                if isinstance(match, tuple):
                    education_requirements.append(match[0])
                else:
                    education_requirements.append(match)
    
    return {
        'required_skills': list(set(required_skills)),
        'preferred_skills': list(set(preferred_skills)),
        'experience_requirements': list(set(experience_requirements)),
        'education_requirements': list(set(education_requirements))
    }

def calculate_job_fit_score(resume_path: str, job_description: str) -> float:
    """
    Calculate a fit score between a resume and a job description based on keyword matching.
    
    Args:
        resume_path: Path to the resume file
        job_description: Job description text
        
    Returns:
        Fit score between 0.0 and 1.0
    """
    try:
        # Extract text from resume
        resume_text = extract_text_from_resume(resume_path)
        if not resume_text:
            logger.error(f"Failed to extract text from resume: {resume_path}")
            return 0.0
        
        # Extract keywords from resume and job description
        resume_keywords = extract_keywords_from_text(resume_text)
        job_requirements = extract_job_requirements(job_description)
        
        # Calculate match score for required skills
        required_skills = set(job_requirements['required_skills'])
        resume_skills = set(resume_keywords['skills'])
        
        if not required_skills:
            required_match_score = 1.0  # No required skills specified
        else:
            required_matches = required_skills.intersection(resume_skills)
            required_match_score = len(required_matches) / len(required_skills)
        
        # Calculate match score for preferred skills
        preferred_skills = set(job_requirements['preferred_skills'])
        if not preferred_skills:
            preferred_match_score = 1.0  # No preferred skills specified
        else:
            preferred_matches = preferred_skills.intersection(resume_skills)
            preferred_match_score = len(preferred_matches) / len(preferred_skills)
        
        # Calculate overall fit score (required skills are weighted more heavily)
        fit_score = (required_match_score * 0.7) + (preferred_match_score * 0.3)
        
        # Use TF-IDF and cosine similarity as an additional measure
        tfidf_vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf_vectorizer.fit_transform([resume_text, job_description])
        cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        # Combine keyword matching score with cosine similarity
        combined_score = (fit_score * 0.7) + (cosine_sim * 0.3)
        
        return min(max(combined_score, 0.0), 1.0)  # Ensure score is between 0 and 1
        
    except Exception as e:
        logger.exception(f"Error calculating job fit score: {str(e)}")
        return 0.0

def get_missing_skills(resume_path: str, job_description: str) -> List[str]:
    """
    Identify skills mentioned in the job description that are missing from the resume.
    
    Args:
        resume_path: Path to the resume file
        job_description: Job description text
        
    Returns:
        List of missing skills
    """
    try:
        # Extract text from resume
        resume_text = extract_text_from_resume(resume_path)
        if not resume_text:
            logger.error(f"Failed to extract text from resume: {resume_path}")
            return []
        
        # Extract keywords from resume and job description
        resume_keywords = extract_keywords_from_text(resume_text)
        job_requirements = extract_job_requirements(job_description)
        
        # Identify missing required skills
        required_skills = set(job_requirements['required_skills'])
        resume_skills = set(resume_keywords['skills'])
        
        missing_skills = list(required_skills - resume_skills)
        
        return missing_skills
        
    except Exception as e:
        logger.exception(f"Error identifying missing skills: {str(e)}")
        return []
