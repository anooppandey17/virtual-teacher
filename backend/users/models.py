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
        
        # Set default role if not provided
        if 'role' not in extra_fields:
            extra_fields['role'] = User.Role.LEARNER

        # Ensure required fields are included
        required_fields = ['first_name', 'last_name', 'role', 'gender', 'phone_number']
        if extra_fields.get('role') == User.Role.LEARNER:
            required_fields.append('grade')
        
        for field in required_fields:
            if field not in extra_fields:
                raise ValueError(f'The {field} field must be set')

        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('role', User.Role.ADMIN)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('first_name', 'Admin')
        extra_fields.setdefault('last_name', 'User')
        extra_fields.setdefault('gender', User.Gender.OTHER)
        extra_fields.setdefault('phone_number', '')
        extra_fields.setdefault('grade', '')

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

    class Gender(models.TextChoices):
        MALE = 'M', _('Male')
        FEMALE = 'F', _('Female')
        OTHER = 'O', _('Other')

    class Grade(models.TextChoices):
        GRADE_1 = '1', _('Grade 1')
        GRADE_2 = '2', _('Grade 2')
        GRADE_3 = '3', _('Grade 3')
        GRADE_4 = '4', _('Grade 4')
        GRADE_5 = '5', _('Grade 5')
        GRADE_6 = '6', _('Grade 6')
        GRADE_7 = '7', _('Grade 7')
        GRADE_8 = '8', _('Grade 8')
        GRADE_9 = '9', _('Grade 9')
        GRADE_10 = '10', _('Grade 10')
        GRADE_11 = '11', _('Grade 11')
        GRADE_12 = '12', _('Grade 12')

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.LEARNER)
    gender = models.CharField(max_length=1, choices=Gender.choices, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    grade = models.CharField(max_length=2, choices=Grade.choices, blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

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
