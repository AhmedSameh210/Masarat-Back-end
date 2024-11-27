from django.contrib import admin
from .models import Chat, ChatMessage

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'lesson', 'created_at', 'updated_at', 'progress_state_summary')
    list_filter = ('created_at', 'updated_at', 'student', 'lesson')
    search_fields = ('student__username', 'lesson__title', 'id')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    def progress_state_summary(self, obj):
        return str(obj.progress_state)[:50] + "..." if len(str(obj.progress_state)) > 50 else obj.progress_state
    progress_state_summary.short_description = "Progress State Summary"


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'sender_type', 'content_summary', 'time_stamp')
    list_filter = ('sender_type', 'time_stamp')
    search_fields = ('content', 'chat__id', 'sender_type')
    ordering = ('-time_stamp',)
    readonly_fields = ('time_stamp',)
    
    def content_summary(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_summary.short_description = "Content Summary"
