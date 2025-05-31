# users/urls.py

from django.urls import path
from .views import UserProfileView, LearnerProfileView, current_user, get_csrf_token, check_username

urlpatterns = [
    path('csrf/', get_csrf_token),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('learner-profile/', LearnerProfileView.as_view(), name='learner-profile-list'),
    path('learner-profile/<int:pk>/', LearnerProfileView.as_view(), name='learner-profile-detail'),
    path('me/', current_user),
    path('check-username/', check_username, name='check-username'),
]
