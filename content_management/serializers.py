from rest_framework import serializers
from .models import Subject, Lesson,Topic,BaseContent,VideoContent,DynamicContent
from chats.models import Chat

# Subject Serializer with nested lessons and progress_percentage
class SubjectSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.SerializerMethodField()
    lessons = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = [
            'id', 'name', 'code', 'description', 'is_active', 
            'academic_year', 'progress_percentage', 'lessons'
        ]

    def get_progress_percentage(self, obj):
        request = self.context.get('request')
        student = request.user

        lessons = Lesson.objects.filter(subject=obj, is_active=True)
        total_lessons = lessons.count()

        if total_lessons == 0:
            return 0

        completed_lessons = 0
        for lesson in lessons:
            chat = Chat.objects.filter(student=student, lesson=lesson).first()
            if chat and chat.progress_state.get("FINAL_ASSESSMENT_EXAM", {}).get("status") == "completed":
                completed_lessons += 1

        progress_percentage = (completed_lessons / total_lessons) * 100
        return round(progress_percentage, 2)

    def get_lessons(self, obj):
        lessons = Lesson.objects.filter(subject=obj, is_active=True).order_by('order')
        return LessonSerializer(lessons, many=True).data


# Lesson Serializer remains unchanged
class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'subject', 'description', 'order', 
            'duration', 'is_active'
        ]


# Topic Serializer
class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = [
            'id', 'name', 'subject', 'description', 
            'topic_difficulty_level'
        ]


# VideoContent Serializer
class VideoContentSerializer(serializers.ModelSerializer):
    base_content_id = serializers.PrimaryKeyRelatedField(
        queryset=BaseContent.objects.all(), source='base_content', write_only=True
    )
    base_content = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = VideoContent
        fields = ['id', 'base_content', 'base_content_id', 'url']


# DynamicContent Serializer
class DynamicContentSerializer(serializers.ModelSerializer):
    base_content_id = serializers.PrimaryKeyRelatedField(
        queryset=BaseContent.objects.all(), source='base_content', write_only=True
    )
    base_content = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = DynamicContent
        fields = ['id', 'base_content', 'base_content_id', 'url']


from rest_framework import serializers

class ContentSerializer(serializers.ModelSerializer):
    video_contents = VideoContentSerializer(many=False, required=False, read_only=True, source='video_content')
    dynamic_contents = DynamicContentSerializer(many=False, required=False, read_only=True, source='dynamic_content')

    class Meta:
        model = BaseContent
        fields = [
            'id', 'lesson', 'learning_type', 'content_type', 
            'learning_phase', 'difficulty_level', 'description', 
            'topic', 
            'video_contents', 'dynamic_contents'
        ]

    def create(self, validated_data):
        # Pop nested data for video_contents and dynamic_contents if provided
        video_content_data = validated_data.pop('video_contents', None)
        dynamic_content_data = validated_data.pop('dynamic_contents', None)

        # Create BaseContent instance
        base_content = BaseContent.objects.create(**validated_data)

        # Create associated VideoContent or DynamicContent if data is provided
        if video_content_data:
            VideoContent.objects.create(base_content=base_content, **video_content_data)
        elif dynamic_content_data:  # Ensure only one is created based on content_type
            DynamicContent.objects.create(base_content=base_content, **dynamic_content_data)

        return base_content

    def update(self, instance, validated_data):
        # Pop nested data for video_contents and dynamic_contents if provided
        video_content_data = validated_data.pop('video_contents', None)
        dynamic_content_data = validated_data.pop('dynamic_contents', None)

        # Update BaseContent instance
        instance = super().update(instance, validated_data)

        # Update or create VideoContent if data is provided
        if video_content_data:
            VideoContent.objects.update_or_create(
                base_content=instance, defaults=video_content_data
            )
        elif dynamic_content_data:  # Ensure only one is updated based on content_type
            DynamicContent.objects.update_or_create(
                base_content=instance, defaults=dynamic_content_data
            )

        return instance
