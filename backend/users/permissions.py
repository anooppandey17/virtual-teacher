from rest_framework.permissions import BasePermission


class IsRole(BasePermission):
    """
    Checks if the authenticated user has a specific role.
    Usage:
        - Set `required_role` attribute on the view.
        - OR pass role during instantiation.
    """

    required_role = None  # 'learner', 'teacher', 'parent', 'admin'

    def __init__(self, role=None):
        if role:
            self.required_role = role

    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and user.role == self.required_role


class IsOwnerOrRelated(BasePermission):
    """
    Object-level permission to allow access only if:
    - User is the owner (`obj.user`)
    - OR the object is related to the user as teacher/parent
    - OR the user is an admin
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False

        if user.role == 'admin':
            return True  # Admins can access anything

        if hasattr(obj, 'user') and obj.user == user:
            return True

        if user.role == 'teacher' and hasattr(obj, 'teacher') and obj.teacher == user:
            return True

        if user.role == 'parent' and hasattr(obj, 'parent') and obj.parent == user:
            return True

        return False


class IsAdminOrIsSelf(BasePermission):
    """
    Allows full access if:
    - Admin
    - Or the object belongs to the user (obj.user == request.user)
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        return user.is_authenticated and (
            user.role == 'admin' or getattr(obj, 'user', None) == user
        )

class CanViewPrompt(BasePermission):
    """
    Learners can view only their prompts. Parents and teachers can view prompts of learners related to them.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        if user.role == 'admin':
            return True
        if user.role == 'learner':
            return obj.learner == user
        if user.role == 'parent':
            return obj.learner.parent_profile.user == user
        if user.role == 'teacher':
            return obj.learner.teacher_profile.user == user
        return False
