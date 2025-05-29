# prompts/models.py

from django.db import models
from django.conf import settings

class Prompt(models.Model):
    creator    = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.CASCADE,
                                   related_name='prompts')
    user_prompt = models.TextField()
    ai_response = models.TextField(blank=True, null=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prompt by {self.creator.email} @ {self.created_at}"
