"""
Automated application system core functionality.
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import time

from django.utils import timezone
from django.db.models import Q

from ..linkedin_integration.api.client import LinkedInClient
from ..linkedin_integration.models import LinkedInJob, JobApplication
from ..resume_analysis.utils import calculate_job_fit_score, extract_text_from_resume
from ..cover_letter.generator import generate_cover_letter
from ..job_matching.algorithm import find_matching_jobs, auto_apply_to_jobs
from .models import AutomatedApplicationSchedule, AutomatedApplicationRun, AutomatedApplicationRunJob

logger = logging.getLogger(__name__)

def run_automated_application_schedule(schedule_id: int) -> Dict[str, Any]:
    """
    Run an automated application schedule.
    
    Args:
        schedule_id: ID of the schedule to run
        
    Returns:
        Dictionary with results of the automated application run
    """
    try:
        # Get schedule
        schedule = AutomatedApplicationSchedule.objects.get(id=schedule_id)
        
        # Check if schedule is active
        if not schedule.is_active:
            return {
                'success': False,
                'message': f"Schedule '{schedule.name}' is not active",
                'run_id': None
            }
        
        # Check if user has a resume
        user = schedule.user
        if not hasattr(user, 'profile') or not user.profile.resume:
            return {
                'success': False,
                'message': f"User {user.username} does not have a resume",
                'run_id': None
            }
        
        # Create run record
        run = AutomatedApplicationRun.objects.create(
            schedule=schedule,
            status='running',
            start_time=timezone.now()
        )
        
        # Initialize log
        log = [f"Started automated application run for schedule '{schedule.name}' at {run.start_time}"]
        
        try:
            # Find matching jobs
            log.append(f"Searching for jobs with keywords: {schedule.keywords or 'Not specified'}, "
                      f"location: {schedule.location or 'Not specified'}, "
                      f"company: {schedule.company or 'Not specified'}, "
                      f"job type: {schedule.job_type or 'Not specified'}")
            
            matching_jobs = find_matching_jobs(
                user=user,
                keywords=schedule.keywords,
                location=schedule.location,
                company=schedule.company,
                job_type=schedule.job_type,
                min_score=schedule.min_match_score
            )
            
            run.jobs_found = len(matching_jobs)
            log.append(f"Found {run.jobs_found} matching jobs with score >= {schedule.min_match_score}")
            
            # Limit to max applications per run
            matching_jobs = matching_jobs[:schedule.max_applications_per_run]
            log.append(f"Processing up to {len(matching_jobs)} jobs (max per run: {schedule.max_applications_per_run})")
            
            # Process matching jobs
            for match_data in matching_jobs:
                job = match_data['job']
                job_match = match_data['job_match']
                match_score = match_data['match_score']
                
                # Create run job record
                run_job = AutomatedApplicationRunJob.objects.create(
                    run=run,
                    job=job,
                    job_match=job_match,
                    status='pending',
                    match_score=match_score
                )
                
                # Skip if already applied
                if JobApplication.objects.filter(user=user, job=job).exists():
                    run_job.status = 'skipped'
                    run_job.error_message = "Already applied to this job"
                    run_job.processed_at = timezone.now()
                    run_job.save()
                    log.append(f"Skipped job '{job.title}' at '{job.company}' - Already applied")
                    continue
                
                # Generate cover letter
                resume_path = user.profile.resume.path
                cover_letter = generate_cover_letter(
                    resume_path=resume_path,
                    job_description=job.description,
                    applicant_name=user.get_full_name() or user.username,
                    job_title=job.title,
                    company_name=job.company
                )
                
                # Apply for job
                client = LinkedInClient()
                user_profile = {
                    'id': user.id,
                    'name': user.get_full_name() or user.username,
                    'email': user.email,
                    'resume_path': resume_path
                }
                
                run.applications_attempted += 1
                
                # Submit application
                result = client.apply_for_job(job.job_id, user_profile, cover_letter)
                run_job.processed_at = timezone.now()
                
                if result['success']:
                    # Create application record
                    application = JobApplication.objects.create(
                        user=user,
                        job=job,
                        cover_letter=cover_letter,
                        resume_used=user.profile.resume,
                        fit_score=match_score,
                        status='submitted',
                        application_id=result['data'].get('application_id')
                    )
                    
                    # Update run job
                    run_job.status = 'applied'
                    run_job.application = application
                    run_job.save()
                    
                    # Update job match
                    job_match.status = 'applied'
                    job_match.save()
                    
                    run.applications_successful += 1
                    log.append(f"Successfully applied to '{job.title}' at '{job.company}'")
                else:
                    # Update run job
                    run_job.status = 'failed'
                    run_job.error_message = result['message']
                    run_job.save()
                    
                    log.append(f"Failed to apply to '{job.title}' at '{job.company}': {result['message']}")
                
                # Add delay between applications to avoid rate limiting
                time.sleep(2)
            
            # Update schedule statistics
            schedule.last_run = run.start_time
            schedule.total_applications += run.applications_attempted
            schedule.successful_applications += run.applications_successful
            
            # Calculate next run time
            if schedule.frequency == 'daily':
                schedule.next_run = timezone.now().replace(
                    hour=schedule.time_of_day.hour,
                    minute=schedule.time_of_day.minute,
                    second=0,
                    microsecond=0
                ) + timedelta(days=1)
            elif schedule.frequency == 'weekly':
                # Find next day of week to run
                today = timezone.now().weekday()  # 0 is Monday
                days_of_week = sorted(schedule.days_of_week)
                
                next_day = None
                for day in days_of_week:
                    if day > today:
                        next_day = day
                        break
                
                if next_day is None and days_of_week:
                    # Wrap around to next week
                    next_day = days_of_week[0]
                    days_ahead = 7 - today + next_day
                else:
                    days_ahead = next_day - today
                
                if next_day is not None:
                    schedule.next_run = timezone.now().replace(
                        hour=schedule.time_of_day.hour,
                        minute=schedule.time_of_day.minute,
                        second=0,
                        microsecond=0
                    ) + timedelta(days=days_ahead)
            
            schedule.save()
            
            # Complete run
            run.status = 'completed'
            run.end_time = timezone.now()
            log.append(f"Completed run at {run.end_time}. "
                      f"Applied to {run.applications_successful}/{run.applications_attempted} jobs.")
            run.log = "\n".join(log)
            run.save()
            
            return {
                'success': True,
                'message': f"Successfully completed automated application run. "
                          f"Applied to {run.applications_successful}/{run.applications_attempted} jobs.",
                'run_id': run.id
            }
            
        except Exception as e:
            logger.exception(f"Error in automated application run: {str(e)}")
            
            # Update run with error
            run.status = 'failed'
            run.end_time = timezone.now()
            run.error_message = str(e)
            log.append(f"Error: {str(e)}")
            run.log = "\n".join(log)
            run.save()
            
            return {
                'success': False,
                'message': f"Error in automated application run: {str(e)}",
                'run_id': run.id
            }
            
    except AutomatedApplicationSchedule.DoesNotExist:
        return {
            'success': False,
            'message': f"Schedule with ID {schedule_id} does not exist",
            'run_id': None
        }
    except Exception as e:
        logger.exception(f"Error running automated application schedule: {str(e)}")
        return {
            'success': False,
            'message': f"Error running automated application schedule: {str(e)}",
            'run_id': None
        }

def calculate_next_run_times():
    """
    Calculate next run times for all active schedules.
    """
    try:
        # Get all active schedules
        schedules = AutomatedApplicationSchedule.objects.filter(is_active=True)
        
        for schedule in schedules:
            # Skip if next run is already set
            if schedule.next_run and schedule.next_run > timezone.now():
                continue
            
            # Calculate next run time
            now = timezone.now()
            
            if schedule.frequency == 'daily':
                # Set to today at specified time
                next_run = now.replace(
                    hour=schedule.time_of_day.hour,
                    minute=schedule.time_of_day.minute,
                    second=0,
                    microsecond=0
                )
                
                # If that time has passed today, set to tomorrow
                if next_run <= now:
                    next_run += timedelta(days=1)
            
            elif schedule.frequency == 'weekly':
                # Get days of week (0-6, where 0 is Monday)
                days_of_week = sorted(schedule.days_of_week)
                
                if not days_of_week:
                    # Default to Monday if no days specified
                    days_of_week = [0]
                
                # Find next day to run
                today = now.weekday()
                next_day = None
                
                for day in days_of_week:
                    if day > today:
                        next_day = day
                        break
                
                if next_day is None:
                    # Wrap around to next week
                    next_day = days_of_week[0]
                    days_ahead = 7 - today + next_day
                else:
                    days_ahead = next_day - today
                
                # Set next run time
                next_run = now.replace(
                    hour=schedule.time_of_day.hour,
                    minute=schedule.time_of_day.minute,
                    second=0,
                    microsecond=0
                ) + timedelta(days=days_ahead)
                
                # If today is a run day but the time has passed, check if there's another run day this week
                if today in days_of_week and schedule.time_of_day.hour <= now.hour and schedule.time_of_day.minute <= now.minute:
                    for day in days_of_week:
                        if day > today:
                            next_day = day
                            days_ahead = next_day - today
                            next_run = now.replace(
                                hour=schedule.time_of_day.hour,
                                minute=schedule.time_of_day.minute,
                                second=0,
                                microsecond=0
                            ) + timedelta(days=days_ahead)
                            break
            
            else:  # custom
                # For custom schedules, just set next run to tomorrow at the specified time
                next_run = now.replace(
                    hour=schedule.time_of_day.hour,
                    minute=schedule.time_of_day.minute,
                    second=0,
                    microsecond=0
                ) + timedelta(days=1)
            
            # Update schedule
            schedule.next_run = next_run
            schedule.save()
            
    except Exception as e:
        logger.exception(f"Error calculating next run times: {str(e)}")

def get_due_schedules():
    """
    Get schedules that are due to run.
    
    Returns:
        List of schedule IDs that are due to run
    """
    try:
        now = timezone.now()
        
        # Get active schedules with next_run in the past or null
        due_schedules = AutomatedApplicationSchedule.objects.filter(
            is_active=True
        ).filter(
            Q(next_run__lte=now) | Q(next_run__isnull=True)
        )
        
        return [schedule.id for schedule in due_schedules]
        
    except Exception as e:
        logger.exception(f"Error getting due schedules: {str(e)}")
        return []
