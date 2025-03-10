import logging
from rest_framework.response import Response
from rest_framework import status
import time
import functools
from django.conf import settings

logger = logging.getLogger(__name__)

class APIErrorResponse:
    """Helper class to format consistent API error responses"""
    
    @staticmethod
    def bad_request(message, errors=None):
        """Return a 400 Bad Request response"""
        response_data = {
            "status": "error",
            "message": message,
            "code": "bad_request"
        }
        if errors:
            response_data["errors"] = errors
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    
    @staticmethod
    def not_found(message="Resource not found"):
        """Return a 404 Not Found response"""
        return Response({
            "status": "error",
            "message": message,
            "code": "not_found"
        }, status=status.HTTP_404_NOT_FOUND)
    
    @staticmethod
    def server_error(message="An unexpected error occurred"):
        """Return a 500 Server Error response"""
        return Response({
            "status": "error",
            "message": message,
            "code": "server_error"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @staticmethod
    def unauthorized(message="Authentication required"):
        """Return a 401 Unauthorized response"""
        return Response({
            "status": "error",
            "message": message,
            "code": "unauthorized"
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    @staticmethod
    def forbidden(message="You don't have permission to perform this action"):
        """Return a 403 Forbidden response"""
        return Response({
            "status": "error",
            "message": message,
            "code": "forbidden"
        }, status=status.HTTP_403_FORBIDDEN)

def timer_decorator(func):
    """Decorator to measure and log function execution time"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Log execution time if it's above threshold (useful for performance monitoring)
        threshold = getattr(settings, 'SLOW_EXECUTION_THRESHOLD_SECONDS', 1.0)
        if execution_time > threshold:
            logger.warning(
                f"Slow execution detected: {func.__module__}.{func.__name__} "
                f"took {execution_time:.2f} seconds"
            )
        return result
    return wrapper
