"""
Views for resume analysis functionality.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages

from .utils import extract_text_from_resume, extract_keywords_from_text, calculate_job_fit_score, get_missing_skills
from .models import ResumeKeywords, JobKeywords
from ..linkedin_integration.models import LinkedInJob

import logging

logger = logging.getLogger(__name__)

@login_required
def analyze_resume(request):
    """
    View for analyzing user's resume and extracting keywords.
    """
    if not hasattr(request.user, 'profile') or not request.user.profile.resume:
        messages.error(request, "Please upload your resume first")
        return redirect('profile_edit')
    
    try:
        # Extract text from resume
        resume_path = request.user.profile.resume.path
        resume_text = extract_text_from_resume(resume_path)
        
        if not resume_text:
            messages.error(request, "Could not extract text from your resume. Please ensure it's a valid PDF or DOCX file.")
            return redirect('profile_edit')
        
        # Extract keywords from resume
        keywords = extract_keywords_from_text(resume_text)
        
        # Save or update resume keywords
        resume_keywords, created = ResumeKeywords.objects.update_or_create(
            user=request.user,
            defaults={
                'skills': keywords['skills'],
                'experience': keywords['experience'],
                'education': keywords['education'],
                'certifications': [],  # Not extracted in current implementation
                'languages': keywords['languages']
            }
        )
        
        if created:
            messages.success(request, "Resume analysis completed successfully!")
        else:
            messages.success(request, "Resume analysis updated successfully!")
        
        return render(request, 'resume_analysis/results.html', {
            'keywords': keywords,
            'resume_text': resume_text[:500] + '...' if len(resume_text) > 500 else resume_text
        })
        
    except Exception as e:
        logger.exception(f"Error analyzing resume: {str(e)}")
        messages.error(request, f"Error analyzing resume: {str(e)}")
        return redirect('profile_edit')

@login_required
def job_match_analysis(request, job_id):
    """
    View for analyzing match between user's resume and a specific job.
    """
    if not hasattr(request.user, 'profile') or not request.user.profile.resume:
        messages.error(request, "Please upload your resume first")
        return redirect('profile_edit')
    
    job = LinkedInJob.objects.get(id=job_id)
    
    try:
        # Calculate job fit score
        resume_path = request.user.profile.resume.path
        fit_score = calculate_job_fit_score(resume_path, job.description)
        
        # Get missing skills
        missing_skills = get_missing_skills(resume_path, job.description)
        
        # Extract job requirements
        from .utils import extract_job_requirements
        job_requirements = extract_job_requirements(job.description)
        
        # Get resume keywords
        resume_keywords = ResumeKeywords.objects.filter(user=request.user).first()
        if not resume_keywords:
            # Analyze resume if not already analyzed
            resume_text = extract_text_from_resume(resume_path)
            keywords = extract_keywords_from_text(resume_text)
            resume_keywords = ResumeKeywords.objects.create(
                user=request.user,
                skills=keywords['skills'],
                experience=keywords['experience'],
                education=keywords['education'],
                languages=keywords['languages']
            )
        
        # Save job keywords if not already saved
        job_keywords, created = JobKeywords.objects.get_or_create(
            job=job,
            defaults={
                'required_skills': job_requirements['required_skills'],
                'preferred_skills': job_requirements['preferred_skills'],
                'experience_requirements': job_requirements['experience_requirements'],
                'education_requirements': job_requirements['education_requirements']
            }
        )
        
        return render(request, 'resume_analysis/job_match.html', {
            'job': job,
            'fit_score': fit_score,
            'missing_skills': missing_skills,
            'job_requirements': job_requirements,
            'resume_keywords': {
                'skills': resume_keywords.skills,
                'experience': resume_keywords.experience,
                'education': resume_keywords.education,
                'languages': resume_keywords.languages
            }
        })
        
    except Exception as e:
        logger.exception(f"Error analyzing job match: {str(e)}")
        messages.error(request, f"Error analyzing job match: {str(e)}")
        return redirect('job_detail', job_id=job_id)

@login_required
def batch_analyze_jobs(request):
    """
    View for batch analyzing multiple jobs against user's resume.
    """
    if not hasattr(request.user, 'profile') or not request.user.profile.resume:
        messages.error(request, "Please upload your resume first")
        return redirect('profile_edit')
    
    # Get recent jobs
    recent_jobs = LinkedInJob.objects.all().order_by('-created_at')[:20]
    
    results = []
    for job in recent_jobs:
        try:
            # Calculate job fit score
            resume_path = request.user.profile.resume.path
            fit_score = calculate_job_fit_score(resume_path, job.description)
            
            results.append({
                'job': job,
                'fit_score': fit_score
            })
        except Exception as e:
            logger.exception(f"Error analyzing job {job.id}: {str(e)}")
    
    # Sort by fit score (highest first)
    results.sort(key=lambda x: x['fit_score'], reverse=True)
    
    return render(request, 'resume_analysis/batch_results.html', {
        'results': results
    })

@login_required
def api_calculate_fit_score(request):
    """
    API endpoint for calculating job fit score.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    if not hasattr(request.user, 'profile') or not request.user.profile.resume:
        return JsonResponse({'error': 'No resume found'}, status=400)
    
    job_id = request.POST.get('job_id')
    if not job_id:
        return JsonResponse({'error': 'Job ID is required'}, status=400)
    
    try:
        job = LinkedInJob.objects.get(id=job_id)
        resume_path = request.user.profile.resume.path
        fit_score = calculate_job_fit_score(resume_path, job.description)
        missing_skills = get_missing_skills(resume_path, job.description)
        
        return JsonResponse({
            'success': True,
            'fit_score': fit_score,
            'missing_skills': missing_skills
        })
    except LinkedInJob.DoesNotExist:
        return JsonResponse({'error': 'Job not found'}, status=404)
    except Exception as e:
        logger.exception(f"Error calculating fit score: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
