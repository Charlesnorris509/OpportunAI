from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        return obj.user == request.user

class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to view or edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Permissions are only allowed to the owner
        return hasattr(obj, 'user') and obj.user == request.user

class ReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow read-only operations.
    """
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
