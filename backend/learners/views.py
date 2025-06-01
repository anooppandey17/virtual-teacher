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
            user_message = Response.objects.create(
                prompt=conversation,
                role='user',
                text=conversation.text
            )

            ai_response = generate_ai_response(user_message.text)
            try:
                Response.objects.create(
                    prompt=conversation,
                    role='assistant',
                    text=ai_response
                )
            except Exception as e:
                print(f"Error saving response: {str(e)}")   

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
            user_message = Response.objects.create(
                prompt=conversation,
                role='user',
                text=conversation.text
            )

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

        if self.request.user.role == 'LEARNER' and conversation.learner != self.request.user:
            raise PermissionDenied("You don't have access to this conversation.")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_message = serializer.save(
            prompt=conversation,
            role='user'
        )

        stream = request.query_params.get('stream', 'false').lower() == 'true'

        if stream:
            ai_stream = generate_ai_response(user_message.text, stream=True)

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
            ai_response = generate_ai_response(user_message.text, stream=False)
            ai_message = Response.objects.create(
                prompt=conversation,
                role='assistant',
                text=ai_response
            )
            conversation.save()

            return DRFResponse({
                'user_message': serializer.data,
                'ai_message': ResponseSerializer(ai_message).data
            })
