from django.contrib import admin
from .models import Setting, Parent, StudentProfile, UserLessonProgress, SchoolApplication


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    list_display = ('user', 'camera_on_or_off', 'theme', 'sound_level')
    list_filter = ('camera_on_or_off', 'theme')
    search_fields = ('user__username',)
    ordering = ('user__username',)


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('email', 'phone_number', 'created_at', 'updated_at')
    search_fields = ('email', 'phone_number')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'academic_year', 'learning_type', 'first_time_login', 'phone_number', 'gender', 'date_of_birth', 'major')
    list_filter = ('academic_year', 'learning_type', 'first_time_login', 'gender', 'major')
    search_fields = ('user__username', 'phone_number', 'parent__email')
    ordering = ('user__username',)


@admin.register(UserLessonProgress)
class UserLessonProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'lesson', 'study_level', 'updated_at')
    list_filter = ('study_level',)
    search_fields = ('user__username', 'lesson__title')
    ordering = ('-updated_at',)
    readonly_fields = ('updated_at',)


@admin.register(SchoolApplication)
class SchoolApplicationAdmin(admin.ModelAdmin):
    list_display = ('role', 'applicant_name', 'applicant_email', 'school_name', 'school_country')
    list_filter = ('role', 'school_country')
    search_fields = ('applicant_name', 'applicant_email', 'school_name')
    ordering = ('-applicant_name',)
