# teachers/views.py
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsAdminOrIsSelf
from .models import TeacherProfile
from .serializers import TeacherProfileSerializer

class TeacherProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    GET /api/teachers/<pk>/     → retrieve profile pk
    PUT / PATCH /api/teachers/<pk>/ → update profile pk
    """
    queryset = TeacherProfile.objects.select_related('user').all()
    serializer_class = TeacherProfileSerializer
    permission_classes = [IsAuthenticated, IsAdminOrIsSelf]


class TeacherProfileListCreateView(generics.ListCreateAPIView):
    queryset = TeacherProfile.objects.all()
    serializer_class = TeacherProfileSerializer