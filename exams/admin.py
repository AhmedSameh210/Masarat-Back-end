from django.contrib import admin
from .models import (
    Question, MCQQuestion, TrueFalseQuestion, LongAnswerQuestion, SortingQuestion,
    Exam, ExamQuestion, Concentration
)

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'lesson', 'topic', 'learning_phase', 'blooms_level', 'learning_type', 'question_type', 'difficulty', 'created_at', 'updated_at')
    list_filter = ('learning_phase', 'blooms_level', 'learning_type', 'question_type', 'difficulty', 'created_at', 'updated_at')
    search_fields = ('question_text', 'lesson__title', 'topic__name')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(MCQQuestion)
class MCQQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'correct_answer')
    search_fields = ('question__question_text',)
    ordering = ('-id',)


@admin.register(TrueFalseQuestion)
class TrueFalseQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'correct_answer')
    search_fields = ('question__question_text',)
    ordering = ('-id',)


@admin.register(LongAnswerQuestion)
class LongAnswerQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'correct_answer')
    search_fields = ('question__question_text',)
    ordering = ('-id',)


@admin.register(SortingQuestion)
class SortingQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question',)
    search_fields = ('question__question_text',)
    ordering = ('-id',)


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'lesson', 'chat', 'result', 'exam_type', 'timestamp', 'passed', 'total_questions', 'percentage')
    list_filter = ('exam_type', 'passed', 'timestamp')
    search_fields = ('student__username', 'lesson__title', 'chat__id')
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp',)


@admin.register(ExamQuestion)
class ExamQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'exam', 'question', 'student_answer', 'is_true')
    search_fields = ('exam__id', 'question__question_text')
    ordering = ('-id',)


@admin.register(Concentration)
class ConcentrationAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'subject', 'lesson', 'is_concentrated', 'emotion', 'timestamp')
    list_filter = ('is_concentrated', 'emotion', 'timestamp')
    search_fields = ('student__username', 'lesson__title', 'subject__name')
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp',)
