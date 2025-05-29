# parents/views.py
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsAdminOrIsSelf
from .models import ParentProfile
from .serializers import ParentProfileSerializer

class ParentProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    GET /api/parents/<pk>/     → retrieve profile pk
    PUT / PATCH /api/parents/<pk>/ → update profile pk
    """
    queryset = ParentProfile.objects.select_related('user').all()
    serializer_class = ParentProfileSerializer
    permission_classes = [IsAuthenticated, IsAdminOrIsSelf]
