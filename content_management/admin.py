from django.contrib import admin
from .models import Subject, Lesson, Topic, BaseContent, VideoContent, DynamicContent

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code', 'academic_year', 'is_active', 'created_at', 'updated_at')
    list_filter = ('academic_year', 'is_active', 'created_at', 'updated_at')
    search_fields = ('name', 'code', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'subject', 'order', 'duration', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at', 'updated_at', 'subject')
    search_fields = ('title', 'description', 'subject__name')
    ordering = ('subject', 'order')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'subject', 'topic_difficulty_level', 'created_at', 'updated_at')
    list_filter = ('topic_difficulty_level', 'created_at', 'updated_at', 'subject')
    search_fields = ('name', 'description', 'subject__name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(BaseContent)
class BaseContentAdmin(admin.ModelAdmin):
    list_display = ('id', 'lesson', 'learning_type', 'content_type', 'learning_phase', 'difficulty_level', 'created_at', 'updated_at')
    list_filter = ('learning_type', 'content_type', 'learning_phase', 'difficulty_level', 'created_at', 'updated_at')
    search_fields = ('lesson__title', 'description')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(VideoContent)
class VideoContentAdmin(admin.ModelAdmin):
    list_display = ('id', 'base_content', 'url')
    search_fields = ('id', 'url', 'base_content__lesson__title')
    ordering = ('-id',)


@admin.register(DynamicContent)
class DynamicContentAdmin(admin.ModelAdmin):
    list_display = ('id', 'base_content', 'url')
    search_fields = ('id', 'url', 'base_content__lesson__title')
    ordering = ('-id',)
