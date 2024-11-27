import uuid
from django.db import models
from django.utils import timezone
from masarat.enums import AcademicYear,LearningType,DifficultyLevel,ContentType,ContentLearningPhase


# Models
class Subject(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    academic_year = models.CharField(
        max_length=20, choices=AcademicYear.choices, null=False, blank=False
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Lesson(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    order = models.PositiveIntegerField()
    duration = models.DurationField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Topic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    topic_difficulty_level = models.CharField(
        max_length=12, choices=DifficultyLevel.choices, null=False, blank=False
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class BaseContent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    learning_type = models.CharField(
        max_length=15, choices=LearningType.choices, null=False, blank=False
    )
    content_type = models.CharField(
        max_length=10, choices=ContentType.choices, unique=False, null=False, blank=False
    )
    learning_phase = models.CharField(
        max_length=50, choices=ContentLearningPhase.choices, null=False, blank=False
    )
    difficulty_level = models.CharField(
        max_length=12, choices=DifficultyLevel.choices, null=False, blank=False
    )
    description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Content {self.id} for Lesson {self.lesson}"



class VideoContent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    base_content = models.OneToOneField(
        BaseContent,
        on_delete=models.CASCADE,
        related_name='video_content'  # Define related name
    )
    url = models.TextField()

    def __str__(self):
        return f"VideoContent {self.id}"

class DynamicContent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    base_content = models.OneToOneField(
        BaseContent,
        on_delete=models.CASCADE,
        related_name='dynamic_content'  # Define related name
    )
    url = models.TextField()

    def __str__(self):
        return f"DynamicContent {self.id}"


