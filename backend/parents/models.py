from django.db import models
from users.models import User

# Create your models here.

class ParentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.user.email