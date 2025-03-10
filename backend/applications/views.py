from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import JobApplication, Interview
from .serializers import JobApplicationSerializer, InterviewSerializer
from .services import ApplicationTracker
import logging

logger = logging.getLogger(__name__)

class JobApplicationViewSet(viewsets.ModelViewSet):
    """API endpoint for managing job applications"""
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['status', 'remote_status', 'location']
    ordering_fields = ['created_at', 'application_date', 'company_name', 'job_title']
    search_fields = ['company_name', 'job_title', 'job_description', 'location']

    def get_queryset(self):
        """Return applications for the current user"""
        return JobApplication.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Create a new application linked to current user"""
        serializer.save(user=self.request.user)
        logger.info(f"User {self.request.user.username} created application: {serializer.data.get('job_title')}")

    @action(detail=True, methods=['POST'])
    def update_status(self, request, pk=None):
        """Update application status"""
        try:
            application = self.get_object()
            new_status = request.data.get('status')
            if not new_status:
                return Response({"error": "Status is required"}, status=status.HTTP_400_BAD_REQUEST)
                
            tracker = ApplicationTracker()
            updated_application = tracker.update_status(application.id, new_status)
            serializer = self.get_serializer(updated_application)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error updating application status: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'])
    def stats(self, request):
        """Get application statistics for current user"""
        try:
            tracker = ApplicationTracker()
            stats = tracker.get_application_statistics(request.user)
            return Response(stats)
        except Exception as e:
            logger.error(f"Error getting application stats: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
