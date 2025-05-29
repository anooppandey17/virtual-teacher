# parents/urls.py
from django.urls import path
from .views import ParentProfileDetailView

urlpatterns = [
    path('<int:pk>/', ParentProfileDetailView.as_view(), name='parent-profile-detail'),
]
