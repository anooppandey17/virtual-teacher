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
from django.utils.timezone import now

# Custom permission so only learners can create prompts
class IsLearner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name='Learner').exists()

class LearnerProfileDetailView(generics.RetrieveUpdateAPIView):
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
        
        conversation = serializer.save(learner=self.request.user)

        if conversation.text:

            words = conversation.text.strip().split()
            if len(words) > 5:
                conversation.title = " ".join(words[:5])
            else:
                conversation.title = conversation.text.strip()
            conversation.save()

            # Only create the user message, let frontend handle AI response
            Response.objects.create(
                prompt=conversation,
                role='user',
                text=conversation.text
            )
            
            # Don't generate AI response here - let frontend handle streaming
            # This prevents duplicate messages and allows proper streaming

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
        
        conversation = serializer.save(learner=self.request.user)

        if conversation.text:
            # Only create the user message, let frontend handle AI response
            Response.objects.create(
                prompt=conversation,
                role='user',
                text=conversation.text
            )
            
            # Don't generate AI response here - let frontend handle streaming
            # This prevents duplicate messages and allows proper streaming

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

        if self.request.user.role == 'LEARNER' and conversation.learner != self.request.user:
            raise PermissionDenied("You don't have access to this conversation.")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check if this is the first message in the conversation
        existing_user_messages = Response.objects.filter(prompt=conversation, role='user').count()
        
        # Only create user message if this is not the first message and text is not empty
        user_message = None
        if existing_user_messages == 0:
            # This is the first message, don't create user message since it's already created
            # Use the conversation's text for AI response
            pass
        elif serializer.validated_data.get('text', '').strip():
            # This is a subsequent message, create user message
            user_message = serializer.save(
                prompt=conversation,
                role='user'
            )

        stream = request.query_params.get('stream', 'false').lower() == 'true'

        if stream:
            # Use the user message text if available, otherwise use the conversation's text
            prompt_text = user_message.text if user_message else conversation.text
            
            # Get conversation history for context
            conversation_history = []
            previous_responses = Response.objects.filter(prompt=conversation).order_by('created_at')
            for response in previous_responses:
                conversation_history.append({
                    'role': response.role,
                    'text': response.text,
                    'created_at': response.created_at
                })
            
            # Pass user's grade and conversation history to the AI response generation
            user_grade = self.request.user.grade
            ai_stream = generate_ai_response(prompt_text, stream=True, user_grade=user_grade, conversation_history=conversation_history)

            def stream_and_store():
                accumulated_text = ""
                for chunk in ai_stream:
                    try:
                        data = json.loads(chunk.strip().replace('data: ', ''))
                        if 'text' in data:
                            accumulated_text += data['text']
                        yield chunk
                    except Exception:
                        yield chunk

                if accumulated_text.strip():
                    Response.objects.create(
                        prompt=conversation,
                        role='assistant',
                        text=accumulated_text.strip()
                    )
                    conversation.updated_at = now()
                    conversation.save()

            response = StreamingHttpResponse(
                stream_and_store(),
                content_type='text/event-stream'
            )
            response['Cache-Control'] = 'no-cache'
            response['X-Accel-Buffering'] = 'no'
            return response

        else:
            # Use the user message text if available, otherwise use the conversation's text
            prompt_text = user_message.text if user_message else conversation.text
            
            # Get conversation history for context
            conversation_history = []
            previous_responses = Response.objects.filter(prompt=conversation).order_by('created_at')
            for response in previous_responses:
                conversation_history.append({
                    'role': response.role,
                    'text': response.text,
                    'created_at': response.created_at
                })
            
            # Pass user's grade and conversation history to the AI response generation
            user_grade = self.request.user.grade
            ai_response = generate_ai_response(prompt_text, stream=False, user_grade=user_grade, conversation_history=conversation_history)
            ai_message = Response.objects.create(
                prompt=conversation,
                role='assistant',
                text=ai_response
            )
            conversation.save()

            return DRFResponse({
                'user_message': serializer.data if user_message else None,
                'ai_message': ResponseSerializer(ai_message).data
            })
