# users/serializers.py

from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from .models import User
from dj_rest_auth.registration.serializers import SocialLoginSerializer
from django.contrib.auth import authenticate
from dj_rest_auth.serializers import LoginSerializer
from .models import AdminProfile #, LearnerProfile, ParentProfile, TeacherProfile, 

class CustomRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)
    role = serializers.ChoiceField(choices=User.Role.choices)
    gender = serializers.ChoiceField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])
    phone_number = serializers.CharField(max_length=15)
    grade = serializers.ChoiceField(choices=User.Grade.choices, required=False)

    def validate(self, data):
        data = super().validate(data)
        if data.get('role') == User.Role.LEARNER and not data.get('grade'):
            raise serializers.ValidationError({
                'grade': 'Grade is required for learners'
            })
        return data

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data.update({
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'role': self.validated_data.get('role', ''),
            'gender': self.validated_data.get('gender', ''),
            'phone_number': self.validated_data.get('phone_number', ''),
            'grade': self.validated_data.get('grade', ''),
        })
        return data

    def custom_signup(self, request, user):
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.role = self.cleaned_data.get('role')
        user.gender = self.cleaned_data.get('gender')
        user.phone_number = self.cleaned_data.get('phone_number')
        if user.role == User.Role.LEARNER:
            user.grade = self.cleaned_data.get('grade')
        user.save()

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

        # Try authenticating with username
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
