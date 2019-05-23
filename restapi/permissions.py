from rest_framework import permissions


class RecordingPermissions(permissions.BasePermission):
    message = "You require permissions to delete recordings"

    def has_permission(self, request, view):
        # Allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS or request.method == 'POST':
            return True
        # Don't allow delete or put for now
        if request.method == 'DELETE':
            return False
