from rest_framework import permissions
from profiles.models import Profile, SharedProfilePermission
from authentification.models import CustomUser

class IsAuthenticatedAndProfileRelated(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if obj.author == request.user:
            return True

        if SharedProfilePermission.objects.filter(
            profile=obj.profile,
            shared_with=request.user
        ).exists():
            return True

        return False


class IsStrategyAuthor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.author == request.user