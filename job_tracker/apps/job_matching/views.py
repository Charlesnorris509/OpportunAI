"""
Views for job matching and automated application functionality.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import JobMatchingPreference, JobMatch, AutomatedApplicationLog
from .algorithm import find_matching_jobs, auto_apply_to_jobs, get_job_recommendations
from ..linkedin_integration.models import LinkedInJob, JobApplication

import logging
import json

logger = logging.getLogger(__name__)

@login_required
def matching_preferences(request):
    """
    View for managing job matching preferences.
    """
    # Get or create user preferences
    preferences, created = JobMatchingPreference.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Update preferences
        preferences.minimum_match_score = float(request.POST.get('minimum_match_score', 0.7))
        preferences.enable_auto_apply = request.POST.get('enable_auto_apply') == 'on'
        preferences.auto_apply_threshold = float(request.POST.get('auto_apply_threshold', 0.8))
        preferences.max_daily_applications = int(request.POST.get('max_daily_applications', 5))
        
        # Update job preferences
        preferences.preferred_job_titles = request.POST.get('preferred_job_titles', '').split(',')
        preferences.preferred_locations = request.POST.get('preferred_locations', '').split(',')
        preferences.preferred_companies = request.POST.get('preferred_companies', '').split(',')
        preferences.excluded_companies = request.POST.get('excluded_companies', '').split(',')
        
        # Update notification settings
        preferences.notify_on_match = request.POST.get('notify_on_match') == 'on'
        preferences.notify_on_auto_apply = request.POST.get('notify_on_auto_apply') == 'on'
        
        # Save preferences
        preferences.save()
        
        messages.success(request, "Job matching preferences updated successfully")
        return redirect('matching_preferences')
    
    return render(request, 'job_matching/preferences.html', {
        'preferences': preferences
    })

@login_required
def job_matches(request):
    """
    View for displaying job matches.
    """
    # Get user preferences
    preferences, created = JobMatchingPreference.objects.get_or_create(user=request.user)
    
    # Get job matches
    matches = JobMatch.objects.filter(
        user=request.user,
        match_score__gte=preferences.minimum_match_score
    ).select_related('job').order_by('-match_score')
    
    return render(request, 'job_matching/matches.html', {
        'matches': matches,
        'preferences': preferences
    })

@login_required
def find_matches(request):
    """
    View for finding new job matches.
    """
    if request.method == 'POST':
        keywords = request.POST.get('keywords', '')
        location = request.POST.get('location', '')
        company = request.POST.get('company', '')
        job_type = request.POST.get('job_type', '')
        
        # Get user preferences
        preferences, created = JobMatchingPreference.objects.get_or_create(user=request.user)
        
        # Find matching jobs
        matching_jobs = find_matching_jobs(
            user=request.user,
            keywords=keywords,
            location=location,
            company=company,
            job_type=job_type,
            min_score=preferences.minimum_match_score
        )
        
        if matching_jobs:
            messages.success(request, f"Found {len(matching_jobs)} matching jobs")
        else:
            messages.info(request, "No matching jobs found")
        
        return redirect('job_matches')
    
    return render(request, 'job_matching/find_matches.html')

@login_required
def match_details(request, match_id):
    """
    View for displaying job match details.
    """
    match = get_object_or_404(JobMatch, id=match_id, user=request.user)
    
    # Check if already applied
    application = JobApplication.objects.filter(user=request.user, job=match.job).first()
    
    return render(request, 'job_matching/match_details.html', {
        'match': match,
        'application': application
    })

@login_required
@require_POST
def update_match_status(request, match_id):
    """
    View for updating job match status.
    """
    match = get_object_or_404(JobMatch, id=match_id, user=request.user)
    
    status = request.POST.get('status')
    if status in [s[0] for s in JobMatch.STATUS_CHOICES]:
        match.status = status
        match.save()
        messages.success(request, "Match status updated successfully")
    else:
        messages.error(request, "Invalid status")
    
    return redirect('match_details', match_id=match.id)

@login_required
def auto_apply_dashboard(request):
    """
    View for auto-apply dashboard.
    """
    # Get user preferences
    preferences, created = JobMatchingPreference.objects.get_or_create(user=request.user)
    
    # Get auto-apply logs
    logs = AutomatedApplicationLog.objects.filter(
        user=request.user
    ).select_related('job', 'job_match').order_by('-attempt_date')
    
    # Get eligible matches for auto-apply
    eligible_matches = JobMatch.objects.filter(
        user=request.user,
        match_score__gte=preferences.auto_apply_threshold,
        auto_apply_attempted=False,
        status='new'
    ).select_related('job').order_by('-match_score')
    
    # Get today's application count
    today = timezone.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())
    
    today_applications = AutomatedApplicationLog.objects.filter(
        user=request.user,
        attempt_date__range=(today_start, today_end),
        status__in=['pending', 'success']
    ).count()
    
    return render(request, 'job_matching/auto_apply_dashboard.html', {
        'preferences': preferences,
        'logs': logs,
        'eligible_matches': eligible_matches,
        'today_applications': today_applications,
        'remaining_applications': max(0, preferences.max_daily_applications - today_applications)
    })

@login_required
@require_POST
def run_auto_apply(request):
    """
    View for running auto-apply process.
    """
    # Check if user has a resume
    if not hasattr(request.user, 'profile') or not request.user.profile.resume:
        messages.error(request, "Please upload your resume first")
        return redirect('profile_edit')
    
    # Get user preferences
    preferences, created = JobMatchingPreference.objects.get_or_create(user=request.user)
    
    # Check if auto-apply is enabled
    if not preferences.enable_auto_apply:
        messages.error(request, "Auto-apply is not enabled. Please update your preferences.")
        return redirect('matching_preferences')
    
    # Run auto-apply
    result = auto_apply_to_jobs(request.user)
    
    if result['success']:
        if result['applied_count'] > 0:
            messages.success(request, f"Successfully applied to {result['applied_count']} jobs")
        else:
            messages.info(request, result['message'])
    else:
        messages.error(request, result['message'])
    
    return redirect('auto_apply_dashboard')

@login_required
def job_recommendations(request):
    """
    View for displaying job recommendations.
    """
    # Check if user has a resume
    if not hasattr(request.user, 'profile') or not request.user.profile.resume:
        messages.error(request, "Please upload your resume first")
        return redirect('profile_edit')
    
    # Get recommendations
    recommendations = get_job_recommendations(request.user)
    
    return render(request, 'job_matching/recommendations.html', {
        'recommendations': recommendations
    })

@login_required
def api_get_matches(request):
    """
    API endpoint for getting job matches.
    """
    try:
        # Get user preferences
        preferences, created = JobMatchingPreference.objects.get_or_create(user=request.user)
        
        # Get job matches
        matches = JobMatch.objects.filter(
            user=request.user,
            match_score__gte=preferences.minimum_match_score
        ).select_related('job').order_by('-match_score')
        
        # Format response
        matches_data = []
        for match in matches:
            matches_data.append({
                'id': match.id,
                'job_id': match.job.id,
                'job_title': match.job.title,
                'company': match.job.company,
                'location': match.job.location,
                'match_score': match.match_score,
                'status': match.status,
                'matching_skills': match.matching_skills,
                'missing_skills': match.missing_skills,
                'created_at': match.created_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'matches': matches_data
        })
    except Exception as e:
        logger.exception(f"Error getting job matches: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@login_required
def api_find_matches(request):
    """
    API endpoint for finding new job matches.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        keywords = data.get('keywords', '')
        location = data.get('location', '')
        company = data.get('company', '')
        job_type = data.get('job_type', '')
        
        # Get user preferences
        preferences, created = JobMatchingPreference.objects.get_or_create(user=request.user)
        
        # Find matching jobs
        matching_jobs = find_matching_jobs(
            user=request.user,
            keywords=keywords,
            location=location,
            company=company,
            job_type=job_type,
            min_score=preferences.minimum_match_score
        )
        
        # Format response
        matches_data = []
        for match in matching_jobs:
            matches_data.append({
                'job_id': match['job'].id,
                'job_title': match['job'].title,
                'company': match['job'].company,
                'location': match['job'].location,
                'match_score': match['match_score'],
                'matching_skills': match['matching_skills'],
                'missing_skills': match['missing_skills']
            })
        
        return JsonResponse({
            'success': True,
            'matches': matches_data
        })
    except Exception as e:
        logger.exception(f"Error finding job matches: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)
