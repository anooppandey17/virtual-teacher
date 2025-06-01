# users/views.py

from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.exceptions import ObjectDoesNotExist
from .models import User #, LearnerProfile
from .serializers import (
    UserSerializer, AdminProfileSerializer, #ParentProfileSerializer,
    # LearnerProfileSerializer, TeacherProfileSerializer
)
from .permissions import IsOwnerOrRelated
from learners.models import LearnerProfile
from learners.serializers import LearnerProfileSerializer
from parents.serializers import ParentProfileSerializer
from teachers.serializers import TeacherProfileSerializer
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

User = get_user_model()

@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'message': 'CSRF cookie set'})

@api_view(['GET'])
@permission_classes([AllowAny])
def check_username(request):
    username = request.GET.get('username', '').strip()
    if not username:
        return Response({'detail': 'Username is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    exists = User.objects.filter(username=username).exists()
    if exists:
        return Response({'detail': 'Username is already taken'}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'detail': 'Username is available'}, status=status.HTTP_200_OK)

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def current_user(request):
    if not request.user.is_authenticated:
        return Response({'detail': 'Not authenticated'}, status=401)

    if request.method == 'GET':
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    elif request.method == 'PATCH':
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self, role):
        return {
            User.Role.ADMIN: AdminProfileSerializer,
            User.Role.PARENT: ParentProfileSerializer,
            User.Role.TEACHER: TeacherProfileSerializer,
            User.Role.LEARNER: LearnerProfileSerializer,
        }.get(role)

    def get_user_profile(self, user):
        """
        Returns the related profile instance for a user based on role.
        """
        try:
            if user.role == User.Role.ADMIN:
                return user.admin_profile
            elif user.role == User.Role.PARENT:
                return user.parent_profile
            elif user.role == User.Role.TEACHER:
                return user.teacher_profile
            elif user.role == User.Role.LEARNER:
                return user.learner_profile
        except ObjectDoesNotExist:
            return None

    def get(self, request):
        user = request.user
        profile = self.get_user_profile(user)
        if profile is None:
            return Response({'error': f'{user.role.title()} profile does not exist'}, status=404)

        serializer_class = self.get_serializer_class(user.role)
        if serializer_class is None:
            return Response({'error': 'Invalid role'}, status=400)

        serializer = serializer_class(profile)
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        profile = self.get_user_profile(user)
        if profile is None:
            return Response({'error': f'{user.role.title()} profile does not exist'}, status=404)

        serializer_class = self.get_serializer_class(user.role)
        if serializer_class is None:
            return Response({'error': 'Invalid role'}, status=400)

        serializer = serializer_class(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LearnerProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        user = request.user

        if pk:
            try:
                profile = LearnerProfile.objects.get(pk=pk)
            except LearnerProfile.DoesNotExist:
                return Response({'detail': 'Profile not found'}, status=404)

            # Object-level permission check
            if not IsOwnerOrRelated().has_object_permission(request, self, profile):
                return Response({'detail': 'Access denied.'}, status=403)

            serializer = LearnerProfileSerializer(profile)
            return Response(serializer.data)

        # List of profiles filtered by user role
        if user.role == User.Role.ADMIN:
            profiles = LearnerProfile.objects.all()
        elif user.role == User.Role.LEARNER:
            profiles = LearnerProfile.objects.filter(user=user)
        elif user.role == User.Role.TEACHER:
            profiles = LearnerProfile.objects.filter(teacher=user)
        elif user.role == User.Role.PARENT:
            profiles = LearnerProfile.objects.filter(parent=user)
        else:
            return Response({'detail': 'Not allowed'}, status=403)

        serializer = LearnerProfileSerializer(profiles, many=True)
        return Response(serializer.data)