# DRF Modules
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthor(BasePermission):
    """
    Custom permission to check if the author has an access for object
    """
    message = "This action is available for it's author"

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsReactionOwner(BasePermission):
    """
    Custom permission to check if the reaction belongs to it's authot
    """

    message = "This action is available for author's reaction"

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsAuthorOrReadOnly(BasePermission):
    """
    Custom permission for checking. 
    If it is author, user can delete or change. 
    Other users can only GET
    """

    message = "Changing is available for author"

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user


class IsPostAuthor(BasePermission):
    """
    Checks of the post belongs to its author or not 
    """

    message = "This action belongs to post's author"

    def has_object_permission(self, request, view, obj):
        return obj.post.author == request.user
    

class IsAdminOrReadOnly(BasePermission):
    """
    Safe methods for everyone
    """

    message = "Managing tags and hashtags is available for admin"

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)