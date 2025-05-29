# users/serializers.py

from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from .models import User
from dj_rest_auth.registration.serializers import SocialLoginSerializer
from django.contrib.auth import authenticate
from dj_rest_auth.serializers import LoginSerializer
from .models import AdminProfile #, LearnerProfile, ParentProfile, TeacherProfile, 

class CustomRegisterSerializer(RegisterSerializer):
    full_name = serializers.CharField(max_length=255)
    role = serializers.ChoiceField(choices=User.Role.choices)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data['full_name'] = self.validated_data.get('full_name', '')
        data['role'] = self.validated_data.get('role', User.Role.LEARNER)
        return data

class CustomSocialLoginSerializer(SocialLoginSerializer):
    # you can customize this if needed; otherwise default works
    pass

class UsernameEmailLoginSerializer(serializers.Serializer):
    login    = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        login    = attrs.get('login')
        password = attrs.get('password')
        user = None

        # Try authenticating with email
        user = authenticate(username=login, password=password)
        # If no match, try authenticating with email field
        if user is None:
            user = authenticate(email=login, password=password)
        
        if not user:
            raise serializers.ValidationError("Invalid credentials: username/email or password is incorrect.")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        attrs['user'] = user
        return attrs

class AdminProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminProfile
        fields = '__all__'
        read_only_fields = ['user']
