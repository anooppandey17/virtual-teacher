# learners/urls.py
from django.urls import path
from .views import (
    LearnerProfileDetailView,
    PromptListCreateView,
    ConversationDetailView,
    MessageCreateView
)

urlpatterns = [
    path('<int:pk>/', LearnerProfileDetailView.as_view(), name='learner-profile-detail'),
    path('conversations/', PromptListCreateView.as_view(), name='conversation-list-create'),
    path('conversations/<int:pk>/', ConversationDetailView.as_view(), name='conversation-detail'),
    path('conversations/<int:conversation_id>/messages/', MessageCreateView.as_view(), name='message-create'),
]
