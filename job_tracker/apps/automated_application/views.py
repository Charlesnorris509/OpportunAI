"""
Views for automated application system.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone

from .models import AutomatedApplicationSchedule, AutomatedApplicationRun, AutomatedApplicationRunJob
from .automation import run_automated_application_schedule, calculate_next_run_times

import logging
import json

logger = logging.getLogger(__name__)

@login_required
def schedules_list(request):
    """
    View for listing automated application schedules.
    """
    schedules = AutomatedApplicationSchedule.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'automated_application/schedules.html', {
        'schedules': schedules
    })

@login_required
def create_schedule(request):
    """
    View for creating a new automated application schedule.
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        # Schedule settings
        is_active = request.POST.get('is_active') == 'on'
        frequency = request.POST.get('frequency')
        days_of_week = request.POST.getlist('days_of_week')
        time_hour = int(request.POST.get('time_hour', 0))
        time_minute = int(request.POST.get('time_minute', 0))
        
        # Search criteria
        keywords = request.POST.get('keywords', '')
        location = request.POST.get('location', '')
        company = request.POST.get('company', '')
        job_type = request.POST.get('job_type', '')
        
        # Application limits
        max_applications_per_run = int(request.POST.get('max_applications_per_run', 5))
        min_match_score = float(request.POST.get('min_match_score', 0.8))
        
        if not name:
            messages.error(request, "Schedule name is required")
            return redirect('create_schedule')
        
        # Convert days of week to integers
        days_of_week_int = []
        for day in days_of_week:
            try:
                days_of_week_int.append(int(day))
            except ValueError:
                pass
        
        # Create time of day
        from datetime import time
        time_of_day = time(hour=time_hour, minute=time_minute)
        
        # Create schedule
        schedule = AutomatedApplicationSchedule.objects.create(
            user=request.user,
            name=name,
            description=description,
            is_active=is_active,
            frequency=frequency,
            days_of_week=days_of_week_int,
            time_of_day=time_of_day,
            keywords=keywords,
            location=location,
            company=company,
            job_type=job_type,
            max_applications_per_run=max_applications_per_run,
            min_match_score=min_match_score
        )
        
        # Calculate next run time
        calculate_next_run_times()
        
        messages.success(request, f"Schedule '{name}' created successfully")
        return redirect('schedules_list')
    
    return render(request, 'automated_application/create_schedule.html')

@login_required
def edit_schedule(request, schedule_id):
    """
    View for editing an automated application schedule.
    """
    schedule = get_object_or_404(AutomatedApplicationSchedule, id=schedule_id, user=request.user)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        # Schedule settings
        is_active = request.POST.get('is_active') == 'on'
        frequency = request.POST.get('frequency')
        days_of_week = request.POST.getlist('days_of_week')
        time_hour = int(request.POST.get('time_hour', 0))
        time_minute = int(request.POST.get('time_minute', 0))
        
        # Search criteria
        keywords = request.POST.get('keywords', '')
        location = request.POST.get('location', '')
        company = request.POST.get('company', '')
        job_type = request.POST.get('job_type', '')
        
        # Application limits
        max_applications_per_run = int(request.POST.get('max_applications_per_run', 5))
        min_match_score = float(request.POST.get('min_match_score', 0.8))
        
        if not name:
            messages.error(request, "Schedule name is required")
            return redirect('edit_schedule', schedule_id=schedule_id)
        
        # Convert days of week to integers
        days_of_week_int = []
        for day in days_of_week:
            try:
                days_of_week_int.append(int(day))
            except ValueError:
                pass
        
        # Create time of day
        from datetime import time
        time_of_day = time(hour=time_hour, minute=time_minute)
        
        # Update schedule
        schedule.name = name
        schedule.description = description
        schedule.is_active = is_active
        schedule.frequency = frequency
        schedule.days_of_week = days_of_week_int
        schedule.time_of_day = time_of_day
        schedule.keywords = keywords
        schedule.location = location
        schedule.company = company
        schedule.job_type = job_type
        schedule.max_applications_per_run = max_applications_per_run
        schedule.min_match_score = min_match_score
        schedule.save()
        
        # Calculate next run time
        calculate_next_run_times()
        
        messages.success(request, f"Schedule '{name}' updated successfully")
        return redirect('schedules_list')
    
    return render(request, 'automated_application/edit_schedule.html', {
        'schedule': schedule
    })

@login_required
def delete_schedule(request, schedule_id):
    """
    View for deleting an automated application schedule.
    """
    schedule = get_object_or_404(AutomatedApplicationSchedule, id=schedule_id, user=request.user)
    
    if request.method == 'POST':
        schedule_name = schedule.name
        schedule.delete()
        messages.success(request, f"Schedule '{schedule_name}' deleted successfully")
    
    return redirect('schedules_list')

@login_required
def schedule_details(request, schedule_id):
    """
    View for displaying schedule details and run history.
    """
    schedule = get_object_or_404(AutomatedApplicationSchedule, id=schedule_id, user=request.user)
    
    # Get run history
    runs = AutomatedApplicationRun.objects.filter(schedule=schedule).order_by('-start_time')
    
    return render(request, 'automated_application/schedule_details.html', {
        'schedule': schedule,
        'runs': runs
    })

@login_required
@require_POST
def run_schedule_now(request, schedule_id):
    """
    View for running a schedule immediately.
    """
    schedule = get_object_or_404(AutomatedApplicationSchedule, id=schedule_id, user=request.user)
    
    # Check if user has a resume
    if not hasattr(request.user, 'profile') or not request.user.profile.resume:
        messages.error(request, "Please upload your resume first")
        return redirect('profile_edit')
    
    # Run schedule
    result = run_automated_application_schedule(schedule.id)
    
    if result['success']:
        messages.success(request, result['message'])
    else:
        messages.error(request, result['message'])
    
    return redirect('schedule_details', schedule_id=schedule.id)

@login_required
def run_details(request, run_id):
    """
    View for displaying run details.
    """
    run = get_object_or_404(AutomatedApplicationRun, id=run_id, schedule__user=request.user)
    
    # Get jobs processed in this run
    jobs = AutomatedApplicationRunJob.objects.filter(run=run).select_related('job').order_by('-match_score')
    
    return render(request, 'automated_application/run_details.html', {
        'run': run,
        'jobs': jobs
    })

@login_required
def dashboard(request):
    """
    View for automated application dashboard.
    """
    # Get user's schedules
    schedules = AutomatedApplicationSchedule.objects.filter(user=request.user).order_by('-created_at')
    
    # Get recent runs
    recent_runs = AutomatedApplicationRun.objects.filter(
        schedule__user=request.user
    ).order_by('-start_time')[:10]
    
    # Get statistics
    total_applications = sum(schedule.total_applications for schedule in schedules)
    successful_applications = sum(schedule.successful_applications for schedule in schedules)
    
    # Get upcoming schedules
    upcoming_schedules = AutomatedApplicationSchedule.objects.filter(
        user=request.user,
        is_active=True,
        next_run__isnull=False
    ).order_by('next_run')[:5]
    
    return render(request, 'automated_application/dashboard.html', {
        'schedules': schedules,
        'recent_runs': recent_runs,
        'total_applications': total_applications,
        'successful_applications': successful_applications,
        'upcoming_schedules': upcoming_schedules
    })

@login_required
def api_get_schedules(request):
    """
    API endpoint for getting automated application schedules.
    """
    try:
        schedules = AutomatedApplicationSchedule.objects.filter(user=request.user).order_by('-created_at')
        
        # Format response
        schedules_data = []
        for schedule in schedules:
            schedules_data.append({
                'id': schedule.id,
                'name': schedule.name,
                'is_active': schedule.is_active,
                'frequency': schedule.frequency,
                'next_run': schedule.next_run.isoformat() if schedule.next_run else None,
                'last_run': schedule.last_run.isoformat() if schedule.last_run else None,
                'total_applications': schedule.total_applications,
                'successful_applications': schedule.successful_applications
            })
        
        return JsonResponse({
            'success': True,
            'schedules': schedules_data
        })
    except Exception as e:
        logger.exception(f"Error getting schedules: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)

@login_required
def api_run_schedule(request):
    """
    API endpoint for running a schedule.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        schedule_id = data.get('schedule_id')
        
        if not schedule_id:
            return JsonResponse({'error': 'Schedule ID is required'}, status=400)
        
        # Check if schedule belongs to user
        try:
            schedule = AutomatedApplicationSchedule.objects.get(id=schedule_id, user=request.user)
        except AutomatedApplicationSchedule.DoesNotExist:
            return JsonResponse({'error': 'Schedule not found'}, status=404)
        
        # Run schedule
        result = run_automated_application_schedule(schedule_id)
        
        return JsonResponse(result)
    except Exception as e:
        logger.exception(f"Error running schedule: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)
