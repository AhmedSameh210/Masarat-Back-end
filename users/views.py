from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.template.loader import render_to_string
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Parent, StudentProfile
from .serializers import UserSerializer, RegisterSerializer, ChangePasswordSerializer
from .serializers import SettingSerializer
from .models import Setting

# Register View
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# Logout View with Token Blacklisting
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create a RefreshToken object
            token = RefreshToken(refresh_token)
            # Blacklist the token
            token.blacklist()

            return Response({"message": "User logged out successfully."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

# User Detail View
class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Forgot Password View
class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Generate a password reset token using JWT
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # Send password reset email
        reset_link = f"{request.build_absolute_uri('/users/reset-password/')}{uid}/{token}/"
        mail_subject = "Password Reset Request"
        message = render_to_string('reset_password_email.html', {'reset_link': reset_link, 'username': user.username})
        send_mail(mail_subject, message, 'no-reply@example.com', [email])

        return Response({"message": "Password reset email sent."}, status=status.HTTP_200_OK)

# Reset Password Confirmation View
class ResetPasswordConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        try:
            # Decode the base64-encoded user ID
            decoded_uid = force_str(urlsafe_base64_decode(uidb64))
            # Use the decoded UID to retrieve the user
            user = User.objects.get(pk=decoded_uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Invalid link."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the token is valid
        if not default_token_generator.check_token(user, token):
            return Response({"error": "Token is invalid or has expired."}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the new password from the request
        new_password = request.data.get('new_password')
        if not new_password:
            return Response({"error": "New password is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Set and save the new password
        user.set_password(new_password)
        user.save()

        return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)


# Change Password View
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            request.user.set_password(serializer.data.get('new_password'))
            request.user.save()
            return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# Retrieve User Settings
class RetrieveSettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            settings = Setting.objects.get(user=request.user)
            serializer = SettingSerializer(settings)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Setting.DoesNotExist:
            return Response({"error": "Settings not found."}, status=status.HTTP_404_NOT_FOUND)

# Update User Settings
class UpdateSettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        try:
            settings = Setting.objects.get(user=request.user)
            serializer = SettingSerializer(settings, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Setting.DoesNotExist:
            return Response({"error": "Settings not found."}, status=status.HTTP_404_NOT_FOUND)


from enum import Enum

class TopicEnum(Enum):
    GEOMETRIC_SHAPES_AREAS = 1
    SQUARE_ROOT = 2
    EXPONENTS = 3
    PYTHAGOREAN_THEOREM = 4

# Create a mapping between Arabic names (from DB) and their English equivalents
topic_mapping = {
    "مساحات الأشكال الهندسية": TopicEnum.GEOMETRIC_SHAPES_AREAS,
    "الجذر التربيعي": TopicEnum.SQUARE_ROOT,
    "الأسس": TopicEnum.EXPONENTS,
    "نظرية فيثاغورس": TopicEnum.PYTHAGOREAN_THEOREM
}
from django.http import JsonResponse
from exams.models import Exam,ExamQuestion,Question,Concentration
from masarat.enums import LearningPhase, BloomsLevel,DifficultyLevel,QuestionType,EmotionChoices
import uuid
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from content_management.models import Lesson,Topic
from chats.models import Chat

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def student_dashboard(request):
    user = request.user.student_profile
    lesson_id = uuid.UUID("6675eaf5-2d4c-458f-8bb3-9671ead1a1ab")
    subject_id = uuid.UUID("ecca904c-9041-4e8d-b2e0-fb5be947dc16")

    # Insight 1: Calculate the total time and highest grade for all attempts of the final exam
    final_exams = Exam.objects.filter(
        lesson_id=lesson_id,
        exam_type=LearningPhase.FINAL_ASSESSMENT_EXAM.value,
        student_id=user.id
    )

    if final_exams.exists():
        # Aggregate total time and get the highest grade for all attempts
        final_exam_grade = max(exam.percentage for exam in final_exams)
    else:
        final_exam_grade = "لم ينعقد بعد"





    # Insight 2: Progress Time for Each Phase in ChatA
    try:
        chat = Chat.objects.get(
            lesson_id=lesson_id,
            student_id=request.user.id
        )
        progress_state = chat.progress_state
        total_time_per_phase = {
            phase: details.get("total_time", 0)
            for phase, details in progress_state.items()
            if phase != "Final_After_Improvement"  # Exclude this phase
        }


        # Insight 3: Calculate Progress Percentage
        completed_phases = sum(1 for details in progress_state.values() if details.get("status") == "completed")
        if completed_phases > 1:
            progress_percentage = ((completed_phases - 1) / 10) * 100
        else:
            progress_percentage = 0
    except Chat.DoesNotExist:
        total_time_per_phase = " "
        progress_percentage = 0


    # Ensure progress percentage does not exceed 100
    if progress_percentage > 100:
        progress_percentage = 100
    







# Insight 4: Highest Score for Each Exam Type
    exams = Exam.objects.filter(
        student_id=user.id,
        lesson_id=lesson_id
    ).order_by('exam_type', '-percentage')

    # Track the highest score for each exam_type
    highest_scores = {}
    for exam in exams:
        if exam.exam_type not in highest_scores:
            highest_scores[exam.exam_type] = min(exam.percentage, 100)  # Clamp to 100 if it exceeds


    # If the final exam is completed, add EXERCISES_EXAM score as 75
    if final_exam_grade != "لم ينعقد بعد":
        highest_scores["EXERCISES_EXAM"] = "75.00"

 # Insight 5: Calculate the Percentage of Correctly Answered Questions Per Topic
    # 1. Get all topics for the given subject_id
    topics = Topic.objects.filter(subject_id=subject_id)

    # 2. Get all questions related to these topics
    questions = Question.objects.filter(topic__in=topics)

    # 3. Get answers from ExamQuestion for the current user and current lesson
    exam_questions = ExamQuestion.objects.filter(
        exam__student_id=user.id,
        exam__lesson_id=lesson_id,
        question__in=questions
    )

    # Initialize dictionary to store the results
    topic_percentage = {}

    # Loop through each Arabic topic name and its Enum
    for arabic_name, topic_enum in topic_mapping.items():
        # Use the Arabic topic name for filtering data
        user_exams = Exam.objects.filter(student=user.id)

        # Get all questions linked to those exams and filter by topic name
        topic_questions = Question.objects.filter(
            exam_questions__exam__in=user_exams,
            topic__name=arabic_name
        ).distinct()
        answered_questions = exam_questions.filter(question__topic__name=arabic_name)

        # Count correct and incorrect answers
        total_questions = topic_questions.count()
        correct_answers = answered_questions.filter(is_true=True).count()
        incorrect_answers = answered_questions.filter(is_true=False).count()

        # Calculate the percentage for this topic
        if total_questions > 0:
            correct_percentage = (correct_answers / total_questions) * 100
            incorrect_percentage = (incorrect_answers / total_questions) * 100
        else:
            correct_percentage = 0
            incorrect_percentage = 0

        # Store the result using the English equivalent as the key
        topic_percentage[topic_enum.name] = {
            "correct_percentage": min(correct_percentage, 100),  # Clamp to 100 if it exceeds
            "incorrect_percentage": incorrect_percentage
        }

 # Insight 6: Number of Correct/Incorrect Answers per Bloom's Level
    # Initialize dictionary to store counts per Bloom's level
    blooms_level_percentage = {level: {"correct": 0, "incorrect": 0} for level in BloomsLevel}

    # Get all questions for the given topics categorized by Bloom's level
    questions_by_bloom_level = {level: questions.filter(blooms_level=level) for level in BloomsLevel}

    # Count correct and incorrect answers for each Bloom's level
    for bloom_level, level_questions in questions_by_bloom_level.items():
        answered_questions_for_level = exam_questions.filter(question__blooms_level=bloom_level)

        correct_answers = answered_questions_for_level.filter(is_true=True).count()
        incorrect_answers = answered_questions_for_level.filter(is_true=False).count()

        blooms_level_percentage[bloom_level]["correct"] = correct_answers
        blooms_level_percentage[bloom_level]["incorrect"] = incorrect_answers



  # Define the difficulty levels
    difficulty_levels = [DifficultyLevel.BEGINNER, DifficultyLevel.INTERMEDIATE, DifficultyLevel.ADVANCED]

    # Initialize a dictionary to store the stats
    difficulty_stats = {}

    # Loop through each difficulty level and calculate the stats
    for difficulty in difficulty_levels:
        # Get the questions for the lesson, user, and difficulty level
        questions = Question.objects.filter(
            lesson_id=lesson_id,
            difficulty=difficulty
        )

        # Get the corresponding exam questions for this user and lesson
        exam_questions = ExamQuestion.objects.filter(
            exam__student_id = user.id,
            exam__lesson_id=lesson_id,
            question__in=questions
        )

        # Initialize counters
        correct_count = 0
        incorrect_count = 0

        # Count the correct and incorrect answers for this difficulty level
        for eq in exam_questions:
            if eq.is_true:
                correct_count += 1
            else:
                incorrect_count += 1

        # Calculate the total questions for this difficulty level
        total_count = correct_count + incorrect_count
        if total_count > 0:
            # Calculate the percentage of correct answers
            correct_percentage = (correct_count / total_count) * 100
        else:
            correct_percentage = 0  # No questions answered for this difficulty level

        # Store the stats for this difficulty level
        difficulty_stats[difficulty] = {
            "correct_count": correct_count,
            "incorrect_count": incorrect_count,
            "correct_percentage": correct_percentage
        }

   # Define the question types
    question_types = [
        QuestionType.MULTIPLE_CHOICE,
        QuestionType.TRUE_FALSE,
        QuestionType.LONG_ANSWER,
        QuestionType.SORTING,
    ]

    # Initialize a dictionary to store the stats
    question_type_stats = {}

    # Loop through each question type and calculate the stats
    for question_type in question_types:
        # Get the questions for the lesson, user, and question type
        questions = Question.objects.filter(
            lesson_id=lesson_id,
            question_type=question_type
        )

        # Get the corresponding exam questions for this user and lesson
        exam_questions = ExamQuestion.objects.filter(
            exam__student=user.id,
            exam__lesson_id=lesson_id,
            question__in=questions
        )

        # Initialize counters
        correct_count = 0
        incorrect_count = 0

        # Count the correct and incorrect answers for this question type
        for eq in exam_questions:
            if eq.is_true:
                correct_count += 1
            else:
                incorrect_count += 1

        # Calculate the total questions for this question type
        total_count = correct_count + incorrect_count
        if total_count > 0:
            # Calculate the percentage of correct answers
            correct_percentage = (correct_count / total_count) * 100
        else:
            correct_percentage = 0  # No questions answered for this question type

        # Store the stats for this question type
        question_type_stats[question_type] = {
            "correct_count": correct_count,
            "incorrect_count": incorrect_count,
            "correct_percentage": correct_percentage
        }


 # Retrieve concentration records for the specified student and lesson
    concentration_records = Concentration.objects.filter(
        student=request.user.id,
        lesson_id=lesson_id
    )

    # Count the concentration states
    total_records = concentration_records.count()
    concentrated_count = concentration_records.filter(is_concentrated=True).count()
    not_concentrated_count = concentration_records.filter(is_concentrated=False).count()
    not_attentive_count = concentration_records.filter(emotion=EmotionChoices.Not_Attentive).count()
    other_emotions_count = total_records - not_attentive_count  # Other emotions count

    # Calculate concentration percentage if records exist
    if total_records > 0:
        concentration_percentage = (concentrated_count / total_records) * 100
        not_attentive_percentage = (not_attentive_count / total_records) * 100 if total_records > 0 else 0
        other_emotions_percentage = (other_emotions_count / total_records) * 100 if total_records > 0 else 0

    else:
        concentration_percentage = 0  # No concentration data available
        not_attentive_percentage = 0
        other_emotions_percentage = 0
    # Prepare response data
    concentration_data = {
        "total_records": total_records,
        "concentrated_count": concentrated_count,
        "not_concentrated_count": not_concentrated_count,
        "concentration_percentage": concentration_percentage,
        "not_attentive_count": not_attentive_count,
        "not_attentive_percentage": not_attentive_percentage,
        "attentive_count": other_emotions_count,
        "attentive_percentage": other_emotions_percentage,
    }










    # Filter the exam questions for the specific lesson
    long_answer_exam_questions = ExamQuestion.objects.filter(
        exam__student=user.id,
        exam__lesson_id=lesson_id,
        question__question_type=QuestionType.LONG_ANSWER
    ).select_related('question', 'question__long_answer_question')

    # Collect results in a JSON-like dictionary
    # Collect the result data as a list
    result_data = []
    print(len(long_answer_exam_questions))  # Check the count of matching questions.
    for exam_question in long_answer_exam_questions:
        long_answer = exam_question.question.long_answer_question

        # Determine the feedback message based on correctness
        if exam_question.is_true:
            feedback = "تهانينا ...... قام الطالب بالإجابة على السؤال المقالي بنجاح! إجابة الطالب كانت دقيقة وشاملة، حيث قام بتغطية الكلمات المفتاحية والمصطلحات المهمة والمفاهيم الضرورية التي تمثل جوهر السؤال."
        else:
            feedback = "للأسف ..... قام الطالب بالإجابة على السؤال المقالي بشكل غير صحيح! إجابة الطالب ينقصها الدقة و الشمول، حيث لم يقم  بتغطية الكلمات المفتاحية والمصطلحات المهمة والمفاهيم الضرورية التي تمثل جوهر السؤال."

        # Add the question data to the result
        result_data.append({
            "question_text": exam_question.question.question_text,
            "correct_answer": long_answer.correct_answer,
            "student_answer": exam_question.student_answer,
            "feedback": feedback,
        })














    data = request.data
    parent_password = data.get("parent_password")

    # Prepare restricted and full dashboard data
    restricted_dashboard_data = {
        "final_exam_grade": final_exam_grade,
        "total_time_per_phase": total_time_per_phase,
        "progress_percentage": progress_percentage,
        "highest_scores_per_phase": highest_scores,
        "topic_percentages": topic_percentage,
    }




    full_dashboard_data = {
        **restricted_dashboard_data,
        "blooms_level_percentage": blooms_level_percentage,
        "difficulty_level_percentage": difficulty_stats,
        "questions_type_percentage": question_type_stats,
        "concentration_percentage": concentration_data,
        "long_answer_questions_result_data":result_data
    }

   # Verify parent password if provided
    if parent_password:
        parent = user.parent
        if parent and parent.password == parent_password :
            # Correct password: Return full dashboard data
            return JsonResponse(full_dashboard_data)
        else:
            # Incorrect password: Return restricted data with an error message
            response_data = restricted_dashboard_data
            response_data["error"] = "Wrong password"
            return JsonResponse(response_data, status=403)

    # No parent password provided: Return restricted data only
    return JsonResponse(restricted_dashboard_data)


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN
from .models import StudentProfile
from masarat.enums import LearningType

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_learning_type(request):
    # Get the new learning type from request data
    new_learning_type = request.data.get("learning_type")

    # Validate the learning type
    if new_learning_type not in [choice[0] for choice in LearningType.choices]:
        return Response(
            {"error": "Invalid learning type"},
            status=HTTP_400_BAD_REQUEST
        )

    # Get the user from the token
    user = request.user

    # Check if the user has a StudentProfile
    try:
        student_profile = user.student_profile
    except StudentProfile.DoesNotExist:
        return Response(
            {"error": "Student profile does not exist for this user"},
            status=HTTP_403_FORBIDDEN
        )

    # Update the learning type
    student_profile.learning_type = new_learning_type
    student_profile.save()

    return Response(
        {"message": "Learning type updated successfully", "new_learning_type": new_learning_type},
        status=HTTP_200_OK
    )


from .serializers import SchoolApplicationCustomSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

@api_view(['POST'])
@permission_classes([AllowAny])
def create_school_application(request):
    serializer = SchoolApplicationCustomSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Application submitted successfully!"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
