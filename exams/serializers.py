from rest_framework import serializers
from .models import Question, MCQQuestion, TrueFalseQuestion, LongAnswerQuestion, SortingQuestion
from content_management.models import Lesson, Topic
from masarat.enums import QuestionType
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
