from django.db import models
from django.contrib.auth import get_user_model
from users.models import User

User = get_user_model()

# Create your models here.
class LearnerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='learner_profile')
    grade = models.CharField(max_length=50, default='Grade')
    school = models.CharField(max_length=100, default='School')
    parent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')

    def __str__(self):
        return f"Learner Profile for {self.user.email}"

class LearnerPrompt(models.Model):
    learner = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': User.Role.LEARNER}, related_name='conversations')
    text = models.TextField(blank=True, null=True)
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversation with {self.learner.email}: {self.title or self.text[:50]}"

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = self.text[:50] + ('...' if len(self.text) > 50 else '')
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-updated_at']

class Response(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]

    prompt = models.ForeignKey(LearnerPrompt, on_delete=models.CASCADE, related_name='messages')
    text = models.TextField()
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='assistant')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role} message in conversation with {self.prompt.learner.email}"

    class Meta:
        ordering = ['created_at']