from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not username:
            raise ValueError('The Username field must be set')

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('role', User.Role.ADMIN)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields['is_staff']:
            raise ValueError('Superuser must have is_staff=True.')
        if not extra_fields['is_superuser']:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Admin')
        PARENT = 'PARENT', _('Parent')
        TEACHER = 'TEACHER', _('Teacher')
        LEARNER = 'LEARNER', _('Learner')

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.LEARNER)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'full_name']

    objects = UserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"

# users/models.py

class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    # add admin-specific fields here

# class ParentProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='parent_profile')
#     # e.g., phone_number, number_of_kids, etc.

# class TeacherProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
#     # e.g., subjects, experience_years, etc.

# class LearnerProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='learner_profile')
#     grade = models.CharField(max_length=50, default='Grade')
#     school = models.CharField(max_length=100, default='School')
#     parent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
#     teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    # e.g., grade_level, enrolled_courses, etc.
