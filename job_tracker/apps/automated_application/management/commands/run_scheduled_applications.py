"""
Management command to run scheduled automated applications.
"""
import logging
from django.core.management.base import BaseCommand
from django.utils import timezone

from job_tracker.apps.automated_application.automation import get_due_schedules, run_automated_application_schedule, calculate_next_run_times

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Run scheduled automated applications'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting automated application scheduler'))
        
        # Calculate next run times for schedules that don't have one
        calculate_next_run_times()
        self.stdout.write('Calculated next run times for schedules')
        
        # Get schedules that are due to run
        due_schedules = get_due_schedules()
        self.stdout.write(f'Found {len(due_schedules)} schedules due to run')
        
        # Run each due schedule
        for schedule_id in due_schedules:
            self.stdout.write(f'Running schedule {schedule_id}')
            result = run_automated_application_schedule(schedule_id)
            
            if result['success']:
                self.stdout.write(self.style.SUCCESS(f'Schedule {schedule_id}: {result["message"]}'))
            else:
                self.stdout.write(self.style.ERROR(f'Schedule {schedule_id}: {result["message"]}'))
        
        self.stdout.write(self.style.SUCCESS('Completed automated application scheduler'))
