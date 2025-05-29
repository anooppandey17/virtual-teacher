from rest_framework import serializers
from .models import LearnerProfile, LearnerPrompt, Response

class LearnerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearnerProfile
        fields = '__all__'

class ResponseSerializer(serializers.ModelSerializer):
    prompt = serializers.CharField(write_only=True, required=False)  # For frontend compatibility

    class Meta:
        model = Response
        fields = ['id', 'role', 'text', 'created_at', 'prompt']
        read_only_fields = ['role']

    def validate(self, data):
        if 'prompt' in data:
            data['text'] = data.pop('prompt')
        return data

class ConversationSerializer(serializers.ModelSerializer):
    messages = ResponseSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    prompt = serializers.CharField(write_only=True, required=True, source='text')  # For frontend compatibility

    class Meta:
        model = LearnerPrompt
        fields = ['id', 'title', 'text', 'created_at', 'updated_at', 'messages', 'last_message', 'prompt']
        read_only_fields = ['learner', 'title', 'text']

    def get_last_message(self, obj):
        last_message = obj.messages.last()
        return last_message.text if last_message else None
