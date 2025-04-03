"""
Job matching algorithm and utilities.
"""
import logging
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta

from django.utils import timezone
from django.db.models import Q

from ..resume_analysis.utils import calculate_job_fit_score, get_missing_skills, extract_text_from_resume, extract_keywords_from_text, extract_job_requirements
from ..cover_letter.generator import generate_cover_letter
from ..linkedin_integration.models import LinkedInJob, JobApplication
from ..linkedin_integration.api.client import LinkedInClient
from .models import JobMatchingPreference, JobMatch, AutomatedApplicationLog

logger = logging.getLogger(__name__)

def find_matching_jobs(user, keywords=None, location=None, company=None, job_type=None, min_score=0.7):
    """
    Find jobs that match a user's resume based on keyword matching.
    
    Args:
        user: User object
        keywords: Optional search keywords
        location: Optional location filter
        company: Optional company filter
        job_type: Optional job type filter
        min_score: Minimum match score threshold
        
    Returns:
        List of matching jobs with scores
    """
    try:
        # Check if user has a resume
        if not hasattr(user, 'profile') or not user.profile.resume:
            logger.error(f"User {user.username} does not have a resume")
            return []
        
        # Get user preferences
        preferences, created = JobMatchingPreference.objects.get_or_create(user=user)
        
        # If no specific search criteria provided, use preferences
        if not keywords and preferences.preferred_job_titles:
            keywords = " ".join(preferences.preferred_job_titles[:3])
        
        if not location and preferences.preferred_locations:
            location = preferences.preferred_locations[0]
        
        if not company and preferences.preferred_companies:
            company = preferences.preferred_companies[0]
        
        # Search for jobs
        client = LinkedInClient()
        results = client.search_jobs(
            keywords=keywords or "software developer",  # Default search if nothing specified
            location=location,
            company=company,
            job_type=job_type
        )
        
        if not results['success']:
            logger.error(f"Error searching jobs: {results['message']}")
            return []
        
        # Process jobs and calculate match scores
        matching_jobs = []
        resume_path = user.profile.resume.path
        
        for job_data in results['data'].get('jobs', []):
            # Skip excluded companies
            if preferences.excluded_companies and job_data['company'] in preferences.excluded_companies:
                continue
                
            # Skip if already applied
            job, created = LinkedInJob.objects.get_or_create(
                job_id=job_data['job_id'],
                defaults={
                    'title': job_data['title'],
                    'company': job_data['company'],
                    'location': job_data.get('location'),
                    'description': job_data.get('description', ''),
                    'url': job_data.get('url', '#'),
                    'posted_date': job_data.get('posted_date'),
                    'job_type': job_data.get('job_type'),
                }
            )
            
            # Skip if already applied
            if JobApplication.objects.filter(user=user, job=job).exists():
                continue
            
            # Calculate job fit score
            fit_score = calculate_job_fit_score(
                resume_path=resume_path,
                job_description=job_data.get('description', '')
            )
            
            # Only include if score meets minimum threshold
            if fit_score >= min_score:
                # Get matching and missing skills
                resume_text = extract_text_from_resume(resume_path)
                resume_keywords = extract_keywords_from_text(resume_text)
                job_requirements = extract_job_requirements(job_data.get('description', ''))
                
                matching_skills = list(set(resume_keywords['skills']).intersection(
                    set(job_requirements['required_skills'] + job_requirements['preferred_skills'])
                ))
                
                missing_skills = list(set(job_requirements['required_skills']) - set(resume_keywords['skills']))
                
                # Create or update job match
                job_match, created = JobMatch.objects.update_or_create(
                    user=user,
                    job=job,
                    defaults={
                        'match_score': fit_score,
                        'matching_skills': matching_skills,
                        'missing_skills': missing_skills,
                        'auto_apply_eligible': fit_score >= preferences.auto_apply_threshold,
                    }
                )
                
                matching_jobs.append({
                    'job': job,
                    'match_score': fit_score,
                    'matching_skills': matching_skills,
                    'missing_skills': missing_skills,
                    'job_match': job_match
                })
        
        # Sort by match score (highest first)
        matching_jobs.sort(key=lambda x: x['match_score'], reverse=True)
        
        return matching_jobs
        
    except Exception as e:
        logger.exception(f"Error finding matching jobs: {str(e)}")
        return []

def auto_apply_to_jobs(user):
    """
    Automatically apply to jobs that meet the user's auto-apply criteria.
    
    Args:
        user: User object
        
    Returns:
        Dictionary with results of auto-apply process
    """
    try:
        # Check if user has a resume
        if not hasattr(user, 'profile') or not user.profile.resume:
            return {
                'success': False,
                'message': "User does not have a resume",
                'applied_count': 0,
                'applications': []
            }
        
        # Get user preferences
        preferences, created = JobMatchingPreference.objects.get_or_create(user=user)
        
        # Check if auto-apply is enabled
        if not preferences.enable_auto_apply:
            return {
                'success': False,
                'message': "Auto-apply is not enabled for this user",
                'applied_count': 0,
                'applications': []
            }
        
        # Check daily application limit
        today = timezone.now().date()
        today_start = datetime.combine(today, datetime.min.time())
        today_end = datetime.combine(today, datetime.max.time())
        
        today_applications = AutomatedApplicationLog.objects.filter(
            user=user,
            attempt_date__range=(today_start, today_end),
            status__in=['pending', 'success']
        ).count()
        
        if today_applications >= preferences.max_daily_applications:
            return {
                'success': False,
                'message': f"Daily application limit reached ({preferences.max_daily_applications})",
                'applied_count': 0,
                'applications': []
            }
        
        # Get eligible job matches
        eligible_matches = JobMatch.objects.filter(
            user=user,
            match_score__gte=preferences.auto_apply_threshold,
            auto_apply_attempted=False,
            status='new'
        ).order_by('-match_score')
        
        # Limit to remaining applications for today
        remaining_applications = preferences.max_daily_applications - today_applications
        eligible_matches = eligible_matches[:remaining_applications]
        
        if not eligible_matches:
            return {
                'success': True,
                'message': "No eligible jobs found for auto-apply",
                'applied_count': 0,
                'applications': []
            }
        
        # Apply to eligible jobs
        applied_count = 0
        applications = []
        
        for job_match in eligible_matches:
            try:
                # Mark as attempted
                job_match.auto_apply_attempted = True
                job_match.save()
                
                # Generate cover letter
                resume_path = user.profile.resume.path
                cover_letter = generate_cover_letter(
                    resume_path=resume_path,
                    job_description=job_match.job.description,
                    applicant_name=user.get_full_name() or user.username,
                    job_title=job_match.job.title,
                    company_name=job_match.job.company
                )
                
                # Create application log
                application_log = AutomatedApplicationLog.objects.create(
                    user=user,
                    job=job_match.job,
                    job_match=job_match,
                    status='pending',
                    match_score=job_match.match_score,
                    cover_letter=cover_letter,
                    attempt_date=timezone.now()
                )
                
                # Submit application to LinkedIn
                client = LinkedInClient()
                user_profile = {
                    'id': user.id,
                    'name': user.get_full_name() or user.username,
                    'email': user.email,
                    'resume_path': resume_path
                }
                
                result = client.apply_for_job(job_match.job.job_id, user_profile, cover_letter)
                
                if result['success']:
                    # Create application record
                    application = JobApplication.objects.create(
                        user=user,
                        job=job_match.job,
                        cover_letter=cover_letter,
                        resume_used=user.profile.resume,
                        fit_score=job_match.match_score,
                        status='submitted',
                        application_id=result['data'].get('application_id')
                    )
                    
                    # Update application log
                    application_log.status = 'success'
                    application_log.completion_date = timezone.now()
                    application_log.application = application
                    application_log.save()
                    
                    # Update job match
                    job_match.status = 'auto_applied'
                    job_match.auto_apply_result = "Application submitted successfully"
                    job_match.save()
                    
                    applied_count += 1
                    applications.append({
                        'job': job_match.job,
                        'status': 'success',
                        'application_id': result['data'].get('application_id')
                    })
                else:
                    # Update application log
                    application_log.status = 'failed'
                    application_log.completion_date = timezone.now()
                    application_log.error_message = result['message']
                    application_log.save()
                    
                    # Update job match
                    job_match.auto_apply_result = f"Application failed: {result['message']}"
                    job_match.save()
                    
                    applications.append({
                        'job': job_match.job,
                        'status': 'failed',
                        'error': result['message']
                    })
            
            except Exception as e:
                logger.exception(f"Error auto-applying to job {job_match.job.id}: {str(e)}")
                
                # Update job match
                job_match.auto_apply_result = f"Application error: {str(e)}"
                job_match.save()
                
                applications.append({
                    'job': job_match.job,
                    'status': 'failed',
                    'error': str(e)
                })
        
        return {
            'success': True,
            'message': f"Applied to {applied_count} jobs",
            'applied_count': applied_count,
            'applications': applications
        }
        
    except Exception as e:
        logger.exception(f"Error in auto-apply process: {str(e)}")
        return {
            'success': False,
            'message': f"Error in auto-apply process: {str(e)}",
            'applied_count': 0,
            'applications': []
        }

def get_job_recommendations(user):
    """
    Get job recommendations for a user based on their resume and preferences.
    
    Args:
        user: User object
        
    Returns:
        List of recommended jobs
    """
    try:
        # Check if user has a resume
        if not hasattr(user, 'profile') or not user.profile.resume:
            return []
        
        # Get user preferences
        preferences, created = JobMatchingPreference.objects.get_or_create(user=user)
        
        # Get recent job matches
        recent_matches = JobMatch.objects.filter(
            user=user,
            match_score__gte=preferences.minimum_match_score
        ).order_by('-match_score')[:10]
        
        # If no recent matches, find new matches
        if not recent_matches:
            # Extract keywords from resume
            resume_path = user.profile.resume.path
            resume_text = extract_text_from_resume(resume_path)
            resume_keywords = extract_keywords_from_text(resume_text)
            
            # Use top skills as search keywords
            keywords = " ".join(resume_keywords['skills'][:5])
            
            # Find matching jobs
            matching_jobs = find_matching_jobs(
                user=user,
                keywords=keywords,
                min_score=preferences.minimum_match_score
            )
            
            return [match['job'] for match in matching_jobs]
        
        return [match.job for match in recent_matches]
        
    except Exception as e:
        logger.exception(f"Error getting job recommendations: {str(e)}")
        return []
