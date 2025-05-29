from django.db import models

# Create your models here.

from users.models import User

class AIPrompt(models.Model):
    learner = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': User.Role.LEARNER}, related_name='ai_prompts')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prompt by {self.learner.email} at {self.created_at}"

class Response(models.Model):
    prompt = models.OneToOneField(AIPrompt, on_delete=models.CASCADE, related_name='response')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response to Prompt {self.prompt.id}"
