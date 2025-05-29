# users/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, AdminProfile, ParentProfile, TeacherProfile, LearnerProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == User.Role.ADMIN:
            AdminProfile.objects.create(user=instance)
        elif instance.role == User.Role.PARENT:
            ParentProfile.objects.create(user=instance)
        elif instance.role == User.Role.TEACHER:
            TeacherProfile.objects.create(user=instance)
        elif instance.role == User.Role.LEARNER:
            LearnerProfile.objects.create(user=instance)
