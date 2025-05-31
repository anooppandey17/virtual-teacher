from django.shortcuts import render

from rest_framework import generics, permissions
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsAdminOrIsSelf, CanViewPrompt
from .models import LearnerProfile, LearnerPrompt, Response
from .serializers import (
    LearnerProfileSerializer, 
    ConversationSerializer,
    ResponseSerializer
)
from rest_framework.exceptions import PermissionDenied
from .services import generate_ai_response
from django.http import StreamingHttpResponse
from rest_framework.response import Response as DRFResponse
from rest_framework import status
import json

# Custom permission so only learners can create prompts
class IsLearner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Learner').exists()

class LearnerProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    GET /api/learners/<pk>/     → retrieve profile pk
    PUT / PATCH /api/learners/<pk>/ → update profile pk
    """
    queryset = LearnerProfile.objects.select_related('user').all()
    serializer_class = LearnerProfileSerializer
    permission_classes = [IsAuthenticated, IsAdminOrIsSelf]

class PromptListCreateView(generics.ListCreateAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return LearnerPrompt.objects.all()
        elif user.role == 'LEARNER':
            return LearnerPrompt.objects.filter(learner=user)
        elif user.role == 'TEACHER':
            learner_users = user.students.values_list('user', flat=True)
            return LearnerPrompt.objects.filter(learner__in=learner_users)
        elif user.role == 'PARENT':
            learner_users = user.children.values_list('user', flat=True)
            return LearnerPrompt.objects.filter(learner__in=learner_users)
        return LearnerPrompt.objects.none()

    def perform_create(self, serializer):
        if self.request.user.role != 'LEARNER':
            raise PermissionDenied("Only learners can create conversations.")
        
        # Create the conversation
        conversation = serializer.save(learner=self.request.user)

        # Create the user's message
        user_message = Response.objects.create(
            prompt=conversation,
            role='user',
            text=conversation.text
        )

        # Generate and save AI response
        ai_response = generate_ai_response(user_message.text)
        Response.objects.create(
            prompt=conversation,
            role='assistant',
            text=ai_response
        )

class ResponseListView(generics.ListAPIView):
    serializer_class = ResponseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'LEARNER':
            return Response.objects.filter(prompt__learner=user)
        elif user.role == 'TEACHER':
            learner_users = user.students.values_list('user', flat=True)
            return Response.objects.filter(prompt__learner__in=learner_users)
        elif user.role == 'PARENT':
            learner_users = user.children.values_list('user', flat=True)
            return Response.objects.filter(prompt__learner__in=learner_users)
        return Response.objects.none()

class PromptDetailView(generics.RetrieveAPIView):
    queryset = LearnerPrompt.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated, CanViewPrompt]

class ConversationListCreateView(generics.ListCreateAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return LearnerPrompt.objects.all()
        elif user.role == 'LEARNER':
            return LearnerPrompt.objects.filter(learner=user)
        elif user.role == 'TEACHER':
            learner_users = user.students.values_list('user', flat=True)
            return LearnerPrompt.objects.filter(learner__in=learner_users)
        elif user.role == 'PARENT':
            learner_users = user.children.values_list('user', flat=True)
            return LearnerPrompt.objects.filter(learner__in=learner_users)
        return LearnerPrompt.objects.none()

    def perform_create(self, serializer):
        if self.request.user.role != 'LEARNER':
            raise PermissionDenied("Only learners can create conversations.")
        
        # Create the conversation
        conversation = serializer.save(learner=self.request.user)

        # Create the user's message
        user_message = Response.objects.create(
            prompt=conversation,
            role='user',
            text=conversation.text
        )

        # Generate and save AI response
        ai_response = generate_ai_response(user_message.text)
        Response.objects.create(
            prompt=conversation,
            role='assistant',
            text=ai_response
        )

class ConversationDetailView(generics.RetrieveAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'ADMIN':
            return LearnerPrompt.objects.all()
        elif user.role == 'LEARNER':
            return LearnerPrompt.objects.filter(learner=user)
        elif user.role == 'TEACHER':
            learner_users = user.students.values_list('user', flat=True)
            return LearnerPrompt.objects.filter(learner__in=learner_users)
        elif user.role == 'PARENT':
            learner_users = user.children.values_list('user', flat=True)
            return LearnerPrompt.objects.filter(learner__in=learner_users)
        return LearnerPrompt.objects.none()

class MessageCreateView(generics.CreateAPIView):
    serializer_class = ResponseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        conversation_id = self.kwargs.get('conversation_id')
        conversation = LearnerPrompt.objects.get(id=conversation_id)

        # Check if user has access to this conversation
        if self.request.user.role == 'LEARNER' and conversation.learner != self.request.user:
            raise PermissionDenied("You don't have access to this conversation.")

        # Create user message
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_message = serializer.save(
            prompt=conversation,
            role='user'
        )

        # Check if streaming is requested
        stream = request.query_params.get('stream', 'false').lower() == 'true'
        
        if not stream:
            # Generate and save AI response
            ai_response = generate_ai_response(user_message.text)
            Response.objects.create(
                prompt=conversation,
                role='assistant',
                text=ai_response
            )
            # Update conversation's updated_at timestamp
            conversation.save()
            return DRFResponse(serializer.data)
        else:
            # Start streaming response
            def stream_response():
                collected_response = []
                try:
                    # Get the generator from generate_ai_response
                    response_generator = generate_ai_response(user_message.text, stream=True)
                    
                    # Iterate through the generator
                    for chunk in response_generator:
                        if chunk:  # Only send non-empty chunks
                            collected_response.append(chunk)
                            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
                except Exception as e:
                    print(f"Streaming error: {str(e)}")
                    yield f"data: {json.dumps({'chunk': 'Error generating response'})}\n\n"
                finally:
                    # Save the complete response
                    try:
                        complete_response = ''.join(collected_response)
                        if complete_response:  # Only save if we have a response
                            Response.objects.create(
                                prompt=conversation,
                                role='assistant',
                                text=complete_response
                            )
                            conversation.save()
                    except Exception as e:
                        print(f"Error saving response: {str(e)}")
                    
            response = StreamingHttpResponse(
                streaming_content=stream_response(),
                content_type='text/event-stream'
            )
            response['Cache-Control'] = 'no-cache'
            response['X-Accel-Buffering'] = 'no'
            return response
