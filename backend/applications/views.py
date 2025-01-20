from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import JobApplication
from .serializers import JobApplicationSerializer

class JobApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return JobApplication.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['GET'])
    def stats(self, request):
        applications = self.get_queryset()
        stats = {
            'total_applications': applications.count(),
            'status_breakdown': {
                status: applications.filter(status=status).count() 
                for status, _ in JobApplication.STATUS_CHOICES
            }
        }
        return Response(stats)
