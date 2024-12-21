# services.py

import openai
from django.conf import settings
from .models import *
from datetime import datetime, timedelta

class ApplicationTracker:
    @staticmethod
    def create_application(user, job_data):
        application = JobApplication.objects.create(
            user=user,
            company_name=job_data['company_name'],
            job_title=job_data['job_title'],
            job_description=job_data['job_description'],
            job_location=job_data['job_location'],
            salary_range=job_data.get('salary_range'),
            job_type=job_data['job_type'],
            remote_status=job_data['remote_status'],
            application_url=job_data.get('application_url'),
            status='SAVED'
        )
        return application

    @staticmethod
    def update_status(application_id, new_status):
        application = JobApplication.objects.get(id=application_id)
        application.status = new_status
        if new_status == 'APPLIED' and not application.date_applied:
            application.date_applied = timezone.now()
        application.save()
        return application

    @staticmethod
    def get_application_statistics(user):
        total_applications = JobApplication.objects.filter(user=user).count()
        active_applications = JobApplication.objects.filter(
            user=user,
            status__in=['APPLIED', 'INTERVIEWING']
        ).count()
        interviews = Interview.objects.filter(
            application__user=user,
            date_time__gte=timezone.now()
        ).count()
        offers = JobApplication.objects.filter(
            user=user,
            status='OFFERED'
        ).count()
        
        return {
            'total_applications': total_applications,
            'active_applications': active_applications,
            'upcoming_interviews': interviews,
            'offers': offers
        }

def application_dashboard(request):
    analytics = ApplicationAnalytics()
    stats = analytics.get_user_statistics(request.user)
    timeline = analytics.get_application_timeline(request.user)
    
    context = {
        'stats': stats,
        'timeline': timeline,
    }
    return render(request, 'dashboard.html', context)

class InterviewManager:
    @staticmethod
    def schedule_interview(application_id, interview_data):
        interview = Interview.objects.create(
            application_id=application_id,
            interview_type=interview_data['type'],
            date_time=interview_data['date_time'],
            interviewer_names=interview_data.get('interviewer_names'),
            location=interview_data['location'],
            notes=interview_data.get('notes')
        )
        
        # Update application status
        application = interview.application
        if application.status == 'APPLIED':
            application.status = 'INTERVIEWING'
            application.save()
        
        return interview

    def get_interview_preparation(self, interview_id):
        interview = Interview.objects.get(id=interview_id)
        application = interview.application
        
        # Generate interview prep based on job description and interview type
        prompt = f"""
        Prepare interview questions and tips for:
        Job Title: {application.job_title}
        Company: {application.company_name}
        Interview Type: {interview.interview_type}
        Job Description: {application.job_description}
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an interview preparation expert."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content

class JobRecommendationEngine:
    @staticmethod
    def get_job_recommendations(user):
        preferences = JobSearchPreference.objects.get(user=user)
        user_profile = UserProfile.objects.get(user=user)
        user_skills = UserSkill.objects.filter(user=user_profile)
        
        # Get successful applications (interviews/offers) to learn from
        successful_applications = JobApplication.objects.filter(
            user=user,
            status__in=['INTERVIEWING', 'OFFERED', 'ACCEPTED']
        )
        
        # Use this data to find similar open applications
        similar_jobs = JobApplication.objects.filter(
            job_type=preferences.preferred_job_type,
            remote_status=preferences.preferred_remote_status,
            # Add more filtering based on preferences
        ).exclude(user=user)
        
        return similar_jobs[:5]  # Return top 5 recommendations
