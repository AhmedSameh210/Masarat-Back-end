from django.contrib.auth.models import User
from django.db import models
import uuid
from content_management.models import Lesson  
from masarat.enums import AcademicYear,LearningType,Major,DifficultyLevel



class Setting(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='setting')
    camera_on_or_off = models.BooleanField(default=True)  # True for on, False for off
    theme = models.CharField(
        max_length=10,
        choices=[
            ('white', 'White'),
            ('dark', 'Dark'),
            ('default', 'Default')
        ],
        default='default'
    )
    sound_level = models.IntegerField(default=50)  # Value from 0 to 100

    def __str__(self):
        return f"{self.user.username}'s Settings"




class Parent(models.Model):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    password = models.CharField(max_length=128)  # Store password securely
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email



class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    academic_year = models.CharField(max_length=20, choices=AcademicYear.choices)
    parent = models.ForeignKey('Parent', on_delete=models.SET_NULL, null=True, blank=True)
    learning_type = models.CharField(max_length=20, choices=LearningType.choices)
    first_time_login = models.BooleanField(default=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    major = models.CharField(max_length=20, choices=Major.choices, blank=True, null=True)
    # Add the OneToOneField to link the settings


    def __str__(self):
        return f"{self.user.username}'s Profile"



class UserLessonProgress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)  # Use the imported Lesson model here
    study_level = models.CharField(max_length=15, choices=DifficultyLevel.choices)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"User {self.user.username} - {self.lesson.title}: {self.study_level}"


class SchoolApplication(models.Model):
    role = models.CharField(max_length=50)  # No predefined choices
    applicant_name = models.CharField(max_length=255)
    applicant_phone = models.CharField(max_length=15)
    applicant_job_title = models.CharField(max_length=100)
    applicant_email = models.EmailField()
    school_name = models.CharField(max_length=255)
    school_country = models.CharField(max_length=100)
    school_phone = models.CharField(max_length=15)
    school_email = models.EmailField()

    def __str__(self):
        return f"{self.applicant_name} - {self.school_name}"