import uuid
from django.db import models
from django.contrib.auth.models import User
from content_management.models import Lesson  # Make sure this import is correct


class Chat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chats")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="chats")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    progress_state = models.JSONField(default=dict)  # Stores the progress phases as JSON

    def __str__(self):
        return f"Chat between student {self.student_id} and lesson {self.lesson_id}"


class ChatMessage(models.Model):
    CHAT_SENDER_TYPES = [
        ('student', 'Student'),
        ('system', 'System'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender_type = models.CharField(max_length=20, choices=CHAT_SENDER_TYPES)
    content = models.JSONField()  # Store content as JSON
    time_stamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender_type} in chat {self.chat.id}"




