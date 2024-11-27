from rest_framework import serializers
from .models import ChatMessage

class MessageSerializer(serializers.ModelSerializer):
    content = serializers.JSONField()  # Ensures content is handled as JSON

    class Meta:
        model = ChatMessage
        fields = ['id', 'content', 'sender_type', 'time_stamp']
