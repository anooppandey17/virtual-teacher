from django.db import models
from users.models import User

# Create your models here.

class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    subject = models.CharField(max_length=100)
    school = models.CharField(max_length=255)
    # e.g., subjects, experience_years, etc.

    def __str__(self):
        return self.user.email