from django.urls import path
from .views import TeacherProfileDetailView, TeacherProfileListCreateView

urlpatterns = [
    path('<int:pk>/', TeacherProfileDetailView.as_view(), name='teacher-profile-detail'),
    path('', TeacherProfileListCreateView.as_view(), name='teacher-profile-list-create'),
]
