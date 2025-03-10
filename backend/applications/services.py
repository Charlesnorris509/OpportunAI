from django.utils import timezone
from .models import JobApplication, Interview
from django.db.models import Count
import logging

logger = logging.getLogger(__name__)

class ApplicationTracker:
    """Service for tracking and analyzing job applications"""
    
    @staticmethod
    def create_application(user, job_data):
        """Create a new job application"""
        try:
            application = JobApplication.objects.create(
                user=user,
                company_name=job_data['company_name'],
                job_title=job_data['job_title'],
                job_description=job_data.get('job_description', ''),
                location=job_data.get('location', ''),
                salary_min=job_data.get('salary_min'),
                salary_max=job_data.get('salary_max'),
                remote_status=job_data.get('remote_status'),
                job_posting_url=job_data.get('job_posting_url'),
                status='SAVED'
            )
            logger.info(f"Application created for {user.username}: {application.company_name} - {application.job_title}")
            return application
        except Exception as e:
            logger.error(f"Error creating application for {user.username}: {str(e)}")
            raise

    @staticmethod
    def update_status(application_id, new_status):
        """Update application status"""
        try:
            application = JobApplication.objects.get(id=application_id)
            old_status = application.status
            application.status = new_status
            
            # If status changed to APPLIED and no application date set
            if new_status == 'APPLIED' and not application.application_date:
                application.application_date = timezone.now()
            
            application.save()
            logger.info(f"Application status updated: {application_id} from {old_status} to {new_status}")
            return application
        except JobApplication.DoesNotExist:
            logger.error(f"Application not found: {application_id}")
            raise
        except Exception as e:
            logger.error(f"Error updating application status: {str(e)}")
            raise

    @staticmethod
    def get_application_statistics(user):
        """Get statistics about user's applications"""
        try:
            # Get all applications for user
            applications = JobApplication.objects.filter(user=user)
            
            # Count by status
            status_counts = applications.values('status').annotate(count=Count('status'))
            status_dict = {item['status']: item['count'] for item in status_counts}
            
            # Get upcoming interviews
            upcoming_interviews = Interview.objects.filter(
                application__user=user,
                date_time__gte=timezone.now()
            ).count()
            
            stats = {
                'total_applications': applications.count(),
                'status_breakdown': status_dict,
                'upcoming_interviews': upcoming_interviews,
                'application_rate': applications.filter(
                    created_at__gte=timezone.now() - timezone.timedelta(days=30)
                ).count(),
            }
            
            return stats
        except Exception as e:
            logger.error(f"Error getting application statistics for {user.username}: {str(e)}")
            raise
