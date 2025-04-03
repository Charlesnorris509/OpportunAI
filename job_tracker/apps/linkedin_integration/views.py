"""
Views for LinkedIn job search and application functionality.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone

from .api.client import LinkedInClient
from .models import LinkedInJob, JobApplication, JobSearchQuery
from ..resume_analysis.utils import calculate_job_fit_score
from ..cover_letter.generator import generate_cover_letter

import json
import logging

logger = logging.getLogger(__name__)

@login_required
def job_search(request):
    """
    View for searching LinkedIn jobs.
    """
    if request.method == 'POST':
        keywords = request.POST.get('keywords', '')
        location = request.POST.get('location', '')
        company = request.POST.get('company', '')
        job_type = request.POST.get('job_type', '')
        
        # Save search query for future reference
        JobSearchQuery.objects.create(
            user=request.user,
            keywords=keywords,
            location=location,
            company=company,
            job_type=job_type,
            last_run=timezone.now()
        )
        
        # Perform job search
        client = LinkedInClient()
        results = client.search_jobs(
            keywords=keywords,
            location=location,
            company=company,
            job_type=job_type
        )
        
        if results['success']:
            # Store jobs in database
            jobs_data = []
            for job_data in results['data'].get('jobs', []):
                job, created = LinkedInJob.objects.update_or_create(
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
                
                # Calculate job fit score if user has a resume
                fit_score = 0
                if hasattr(request.user, 'profile') and request.user.profile.resume:
                    fit_score = calculate_job_fit_score(
                        request.user.profile.resume.path, 
                        job_data.get('description', '')
                    )
                
                jobs_data.append({
                    'id': job.id,
                    'job_id': job.job_id,
                    'title': job.title,
                    'company': job.company,
                    'location': job.location,
                    'url': job.url,
                    'posted_date': job.posted_date,
                    'fit_score': fit_score
                })
            
            return render(request, 'linkedin_integration/search_results.html', {
                'jobs': jobs_data,
                'total': results['data'].get('total', 0),
                'keywords': keywords,
                'location': location,
                'company': company,
                'job_type': job_type
            })
        else:
            messages.error(request, f"Error searching jobs: {results['message']}")
            return redirect('dashboard')
    
    # GET request - show search form
    recent_searches = JobSearchQuery.objects.filter(user=request.user).order_by('-last_run')[:5]
    return render(request, 'linkedin_integration/search.html', {
        'recent_searches': recent_searches
    })

@login_required
def job_detail(request, job_id):
    """
    View for displaying job details and application options.
    """
    job = get_object_or_404(LinkedInJob, id=job_id)
    
    # Get detailed job information if needed
    client = LinkedInClient()
    job_details = client.get_job_details(job.job_id)
    
    # Calculate job fit score
    fit_score = 0
    if hasattr(request.user, 'profile') and request.user.profile.resume:
        fit_score = calculate_job_fit_score(
            request.user.profile.resume.path, 
            job.description
        )
    
    # Check if user has already applied
    application = JobApplication.objects.filter(user=request.user, job=job).first()
    
    # Generate cover letter suggestion if not applied yet
    cover_letter = None
    if not application and hasattr(request.user, 'profile') and request.user.profile.resume:
        cover_letter = generate_cover_letter(
            request.user.profile.resume.path,
            job.description,
            request.user.get_full_name(),
            job.title,
            job.company
        )
    
    return render(request, 'linkedin_integration/job_detail.html', {
        'job': job,
        'job_details': job_details.get('data', {}),
        'fit_score': fit_score,
        'application': application,
        'cover_letter': cover_letter
    })

@login_required
@require_POST
def apply_for_job(request, job_id):
    """
    View for applying to a job.
    """
    job = get_object_or_404(LinkedInJob, id=job_id)
    
    # Check if user has already applied
    existing_application = JobApplication.objects.filter(user=request.user, job=job).first()
    if existing_application:
        messages.warning(request, f"You have already applied for this job on {existing_application.application_date}")
        return redirect('job_detail', job_id=job.id)
    
    # Get user profile and resume
    if not hasattr(request.user, 'profile') or not request.user.profile.resume:
        messages.error(request, "You need to upload a resume before applying for jobs")
        return redirect('profile_edit')
    
    # Get cover letter from form
    cover_letter = request.POST.get('cover_letter', '')
    if not cover_letter:
        messages.error(request, "Cover letter is required")
        return redirect('job_detail', job_id=job.id)
    
    # Calculate job fit score
    fit_score = calculate_job_fit_score(
        request.user.profile.resume.path, 
        job.description
    )
    
    # Create application record
    application = JobApplication.objects.create(
        user=request.user,
        job=job,
        cover_letter=cover_letter,
        resume_used=request.user.profile.resume,
        fit_score=fit_score,
        status='pending'
    )
    
    # Submit application to LinkedIn
    client = LinkedInClient()
    user_profile = {
        'id': request.user.id,
        'name': request.user.get_full_name(),
        'email': request.user.email,
        'resume_path': request.user.profile.resume.path
    }
    
    result = client.apply_for_job(job.job_id, user_profile, cover_letter)
    
    if result['success']:
        # Update application with external ID and status
        application.application_id = result['data'].get('application_id')
        application.status = 'submitted'
        application.save()
        
        messages.success(request, "Your application has been submitted successfully!")
    else:
        application.notes = f"Error: {result['message']}"
        application.save()
        messages.error(request, f"Error submitting application: {result['message']}")
    
    return redirect('application_status')

@login_required
def application_status(request):
    """
    View for displaying user's job applications and their status.
    """
    applications = JobApplication.objects.filter(user=request.user).select_related('job')
    
    return render(request, 'linkedin_integration/application_status.html', {
        'applications': applications
    })

@login_required
def auto_apply_jobs(request):
    """
    View for automatically applying to jobs that match the user's profile.
    """
    if not hasattr(request.user, 'profile') or not request.user.profile.resume:
        messages.error(request, "You need to upload a resume before using auto-apply")
        return redirect('profile_edit')
    
    # Get recent job searches
    recent_search = JobSearchQuery.objects.filter(user=request.user).order_by('-last_run').first()
    
    if not recent_search:
        messages.warning(request, "You need to perform a job search before using auto-apply")
        return redirect('job_search')
    
    # Search for jobs
    client = LinkedInClient()
    results = client.search_jobs(
        keywords=recent_search.keywords,
        location=recent_search.location,
        company=recent_search.company,
        job_type=recent_search.job_type
    )
    
    if not results['success']:
        messages.error(request, f"Error searching jobs: {results['message']}")
        return redirect('dashboard')
    
    # Process jobs and auto-apply to matching ones
    applied_count = 0
    for job_data in results['data'].get('jobs', []):
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
        if JobApplication.objects.filter(user=request.user, job=job).exists():
            continue
        
        # Calculate job fit score
        fit_score = calculate_job_fit_score(
            request.user.profile.resume.path, 
            job_data.get('description', '')
        )
        
        # Only apply if fit score is above threshold (e.g., 70%)
        if fit_score >= 0.7:
            # Generate cover letter
            cover_letter = generate_cover_letter(
                request.user.profile.resume.path,
                job_data.get('description', ''),
                request.user.get_full_name(),
                job_data['title'],
                job_data['company']
            )
            
            # Create application record
            application = JobApplication.objects.create(
                user=request.user,
                job=job,
                cover_letter=cover_letter,
                resume_used=request.user.profile.resume,
                fit_score=fit_score,
                status='pending'
            )
            
            # Submit application to LinkedIn
            user_profile = {
                'id': request.user.id,
                'name': request.user.get_full_name(),
                'email': request.user.email,
                'resume_path': request.user.profile.resume.path
            }
            
            result = client.apply_for_job(job.job_id, user_profile, cover_letter)
            
            if result['success']:
                # Update application with external ID and status
                application.application_id = result['data'].get('application_id')
                application.status = 'submitted'
                application.save()
                applied_count += 1
            else:
                application.notes = f"Error: {result['message']}"
                application.save()
    
    if applied_count > 0:
        messages.success(request, f"Successfully auto-applied to {applied_count} matching jobs!")
    else:
        messages.info(request, "No matching jobs found for auto-apply. Try broadening your search criteria.")
    
    return redirect('application_status')
