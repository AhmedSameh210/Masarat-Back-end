import uuid
from django.db import models
from django.utils import timezone
from masarat.enums import LearningType, DifficultyLevel, LearningPhase,BloomsLevel,QuestionType,EmotionChoices
from content_management.models import Lesson, Subject
from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
from chats.models import Chat
from content_management.models import Topic

# Base Question Model
class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    learning_phase = models.CharField(max_length=30, choices=LearningPhase.choices)
    blooms_level = models.CharField(max_length=10, choices=BloomsLevel.choices)
    learning_type = models.CharField(max_length=15, choices=LearningType.choices)
    question_text = models.TextField()
    question_type = models.CharField(max_length=15, choices=QuestionType.choices)
    difficulty = models.CharField(max_length=15, choices=DifficultyLevel.choices)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    cause = models.TextField(blank=True, null=True)
    
    # New field for the question location in video
    question_location_in_video = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.question_text[:50]}..."


# Derived Models for Specific Question Types
class MCQQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='mcq_question')
    choices = models.JSONField()
    correct_answer = models.CharField(max_length=255)

    def __str__(self):
        return f"MCQ {self.question}"


class TrueFalseQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='true_false_question')
    correct_answer = models.BooleanField()

    def __str__(self):
        return f"True/False {self.question}"


class LongAnswerQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='long_answer_question')
    correct_answer = models.TextField()

    def __str__(self):
        return f"Long Answer {self.question}"


class SortingQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.OneToOneField(Question, on_delete=models.CASCADE, related_name='sorting_question')
    correct_order = models.JSONField()

    def __str__(self):
        return f"Sorting {self.question}"

import requests
from content_management.models import BaseContent
from masarat.enums import ContentLearningPhase
from collections import defaultdict
from content_management.serializers import ContentSerializer




from rest_framework import serializers


class MCQQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MCQQuestion
        fields = '__all__'

class TrueFalseQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrueFalseQuestion
        fields = '__all__'

class LongAnswerQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LongAnswerQuestion
        fields = '__all__'

class SortingQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SortingQuestion
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    lesson = serializers.PrimaryKeyRelatedField(queryset=Lesson.objects.all())
    topic = serializers.PrimaryKeyRelatedField(queryset=Topic.objects.all())
    mcq_question = MCQQuestionSerializer(required=False)
    true_false_question = TrueFalseQuestionSerializer(required=False)
    long_answer_question = LongAnswerQuestionSerializer(required=False)
    sorting_question = SortingQuestionSerializer(required=False)

    class Meta:
        model = Question
        fields = [
            'id', 'lesson', 'topic', 'learning_phase', 'blooms_level', 
            'learning_type', 'question_text', 'question_type', 'difficulty', 
            'created_at', 'updated_at', 'cause', 'question_location_in_video',
            'mcq_question', 'true_false_question', 'long_answer_question', 'sorting_question'
        ]

    def to_representation(self, instance):
        # Get the original representation
        representation = super().to_representation(instance)
        
        # Remove unnecessary question types based on `question_type`
        question_type = representation.get('question_type')
        if question_type == QuestionType.MULTIPLE_CHOICE:
            representation.pop('true_false_question', None)
            representation.pop('long_answer_question', None)
            representation.pop('sorting_question', None)
        elif question_type == QuestionType.TRUE_FALSE:
            representation.pop('mcq_question', None)
            representation.pop('long_answer_question', None)
            representation.pop('sorting_question', None)
        elif question_type == QuestionType.LONG_ANSWER:
            representation.pop('mcq_question', None)
            representation.pop('true_false_question', None)
            representation.pop('sorting_question', None)
        elif question_type == QuestionType.SORTING:
            representation.pop('mcq_question', None)
            representation.pop('true_false_question', None)
            representation.pop('long_answer_question', None)
        
        return representation
    
from rest_framework import serializers




class Exam(models.Model):
    

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="exams")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="exams")
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='exams')

    result = models.BigIntegerField()
    exam_type = models.CharField(max_length=30, choices=LearningPhase.choices)  # Updated to use LearningPhase enum
    timestamp = models.DateTimeField(default=timezone.now)

    passed = models.BooleanField(default=False)  # Whether the student passed or not
    total_questions = models.IntegerField()      # Total number of questions in the exam
    percentage = models.DecimalField(max_digits=5, decimal_places=2)  # Percentage of score obtained

    def __str__(self):
        return f"Exam {self.id} by Student {self.student_id}"

    def get_failed_topics_content(self):

        # Step 1: Identify topics with a pass rate below 50%
        exam_questions = ExamQuestion.objects.filter(exam=self).select_related('question')
        topic_stats = defaultdict(lambda: {'total': 0, 'passed': 0})

        for exam_question in exam_questions:
            topic = exam_question.question.topic
            topic_stats[topic]['total'] += 1
            if exam_question.is_true:
                topic_stats[topic]['passed'] += 1

        # Determine topics with less than 50% pass rate
        failed_topics = [
            topic for topic, stats in topic_stats.items()
            if (stats['passed'] / stats['total']) * 100 < 50
        ]




        # Step 2: Retrieve relevant content based on failed topics
        student_learning_type = self.student.student_profile.learning_type
        failed_content = BaseContent.objects.filter(
            lesson=self.lesson,
            learning_type=student_learning_type,
            topic__in=failed_topics,
            difficulty_level=DifficultyLevel.BEGINNER.value
            )

        serialized_data = ContentSerializer(failed_content, many=True).data

        return serialized_data


    def get_failed_topics_for_previous_content(self):

        # Step 1: Identify topics with a pass rate below 50%
        exam_questions = ExamQuestion.objects.filter(exam=self).select_related('question')
        topic_stats = defaultdict(lambda: {'total': 0, 'passed': 0})

        for exam_question in exam_questions:
            topic = exam_question.question.topic
            topic_stats[topic]['total'] += 1
            if exam_question.is_true:
                topic_stats[topic]['passed'] += 1

        # Determine topics with less than 50% pass rate
        failed_topics = [
            topic for topic, stats in topic_stats.items()
            if (stats['passed'] / stats['total']) * 100 < 50
        ]
        # Step 2: Retrieve relevant content based on failed topics
        student_learning_type = self.student.student_profile.learning_type
        failed_content = BaseContent.objects.filter(
            lesson=self.lesson,
            learning_type=student_learning_type,
            topic__in=failed_topics,
            learning_phase=ContentLearningPhase.PREVIOUS_CONTENT_CONTENT.value,
            difficulty_level=DifficultyLevel.BEGINNER.value
        )
        serialized_data = ContentSerializer(failed_content, many=True).data

        return serialized_data





    def get_failed_topics_for_previous_exam(self):


        # Step 1: Identify topics with a pass rate below 50%
        exam_questions = ExamQuestion.objects.filter(exam=self).select_related('question')
        topic_stats = defaultdict(lambda: {'total': 0, 'passed': 0})

        for exam_question in exam_questions:
            topic = exam_question.question.topic
            topic_stats[topic]['total'] += 1
            if exam_question.is_true:
                topic_stats[topic]['passed'] += 1

        # Determine topics with less than 50% pass rate
        failed_topics = [
            topic for topic, stats in topic_stats.items()
            if (stats['passed'] / stats['total']) * 100 < 50
        ]
        # Step 2: Retrieve relevant content based on failed topics
        questions_queryset = Question.objects.filter(
                lesson_id=self.lesson,
                learning_phase=LearningPhase.PREV_REVISION_EXAM.value,
                topic__in=failed_topics,

            ).exclude(
                difficulty=DifficultyLevel.CHALLENGING
            )


        for question in questions_queryset:

            correct_answer = ""
            if hasattr(question, 'mcq_question'):
                correct_answer = question.mcq_question.correct_answer
            elif hasattr(question, 'true_false_question'):
                correct_answer = "True" if question.true_false_question.correct_answer else "False"
            elif hasattr(question, 'long_answer_question'):
                correct_answer = question.long_answer_question.correct_answer
            elif hasattr(question, 'sorting_question'):
                correct_answer = ', '.join(question.sorting_question.correct_order)

            question.cause = f"الإجابة الصحيحة هي: {correct_answer}" + (f", السبب: {question.cause}" if question.cause else "")


        # Serialize the questions
        questions = QuestionSerializer(questions_queryset, many=True).data




        return list(questions) if questions is not None else None










class ExamQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="exam_questions")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="exam_questions")
    student_answer = models.TextField()  # Flexible storage for strings, numbers, booleans as strings, etc.
    is_true = models.BooleanField()

    def __str__(self):
        return f"Question {self.id} in Exam {self.exam_id}"


class Concentration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_concentrated = models.BooleanField()
    emotion = models.CharField(max_length=50, choices=EmotionChoices.choices)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Concentration Record for Student {self.student.username} in Lesson {self.lesson.title} - {self.timestamp}"
    






    
    