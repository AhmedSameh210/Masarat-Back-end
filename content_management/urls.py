from django.urls import path
from .views import (SubjectWithLessonsView,
     SubjectCreateView,
     LessonCreateView, TopicCreateView,
    LessonContentView, ContentCreateView,grade_survey
    # RevisionContentView, RevisionContentCreateView
)

urlpatterns = [
    # Subjects
    path('subjects_with_lessons/', SubjectWithLessonsView.as_view(), name='subject-list'),
    path('subjects/create/', SubjectCreateView.as_view(), name='subject-create'),

    # Lessons
    path('lessons/create/', LessonCreateView.as_view(), name='lesson-create'),

    # Topics
    path('topics/create/', TopicCreateView.as_view(), name='topic-create'),

    # Lesson Content
    path('lessons/<uuid:lesson_id>/contents/', LessonContentView.as_view(), name='lesson-content-list'),
    path('contents/create/', ContentCreateView.as_view(), name='content-create'),
    path('grade_survey/', grade_survey, name='content-create'),
]
