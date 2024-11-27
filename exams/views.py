from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Question, MCQQuestion, TrueFalseQuestion, LongAnswerQuestion, SortingQuestion,Concentration
from .serializers import (
    QuestionSerializer, 
    MCQQuestionSerializer, 
    TrueFalseQuestionSerializer, 
    LongAnswerQuestionSerializer, 
    SortingQuestionSerializer
)
from users.models import  StudentProfile  # Add StudentProfile here
from chats.models import Chat

from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from .models import Concentration
from users.models import StudentProfile, UserLessonProgress
from content_management.models import Lesson, Subject;
from exams.models import LearningPhase;
import requests










class QuestionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        # Return a list of all questions
        queryset = Question.objects.all()
        serializer = QuestionSerializer(queryset, many=True)
        return Response(serializer.data)


    def create(self, request):
    # Create a base question first
        question_data = {
            "lesson": request.data.get('lesson'),  # No _id suffix
            "topic": request.data.get('topic'),    # No _id suffix
            "learning_phase": request.data.get('learning_phase'),
            "blooms_level": request.data.get('blooms_level'),
            "learning_type": request.data.get('learning_type'),
            "question_text": request.data.get('question_text'),
            "question_type": request.data.get('question_type'),
            "difficulty": request.data.get('difficulty'),
        }
        
        question_serializer = QuestionSerializer(data=question_data)
        if question_serializer.is_valid():
            question_instance = question_serializer.save()  # Save the base Question instance
            
            # Now create the specific question type based on the type
            question_type = question_data['question_type']

            if question_type == 'MULTIPLE_CHOICE':
                mcq_data = {
                    "question": question_instance.id,  # Use the saved Question instance
                    "choices": request.data.get('choices'),
                    "correct_answer": request.data.get('correct_answer'),
                }
                serializer = MCQQuestionSerializer(data=mcq_data)
            elif question_type == 'TRUE_FALSE':
                tf_data = {
                    "question": question_instance.id,
                    "correct_answer": request.data.get('correct_answer'),
                }
                serializer = TrueFalseQuestionSerializer(data=tf_data)
            elif question_type == 'LONG_ANSWER':
                la_data = {
                    "question": question_instance.id,
                    "correct_answer": request.data.get('correct_answer'),
                }
                serializer = LongAnswerQuestionSerializer(data=la_data)
            elif question_type == 'SORTING':
                sorting_data = {
                    "question": question_instance.id,
                    "correct_order": request.data.get('correct_order'),
                }
                serializer = SortingQuestionSerializer(data=sorting_data)
            else:
                return Response({'error': 'Invalid question type'}, status=400)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)

        return Response(question_serializer.errors, status=400)











    def retrieve(self, request, pk=None):
        # Retrieve questions for a specific lesson and learning type
        lesson_id = pk
        user = request.user

        # Get the user's learning type from their StudentProfile
        try:
            student_profile = user.student_profile
            learning_type = student_profile.learning_type
        except StudentProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=404)

        # Filter questions by lesson_id and learning_type
        questions = Question.objects.filter(lesson_id=lesson_id, learning_type=learning_type)

        if not questions.exists():
            return Response({'error': 'No questions found for this lesson and learning type'}, status=404)

        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)




# Concntration Api FLask

import base64
import cv2
import numpy as np
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def track_concentration(request):
    user = request.user
    student_profile = StudentProfile.objects.get(user=user)

    # Extract base64 frame, subject_id, and lesson_id from request
    frame_base64 = request.data.get("frame")
    subject_id = request.data.get("subject_id")
    lesson_id = request.data.get("lesson_id")

    if not frame_base64:
        return Response({"error": "Frame data missing"}, status=status.HTTP_400_BAD_REQUEST)
    if not subject_id or not lesson_id:
        return Response({"error": "Subject and Lesson IDs are required"}, status=status.HTTP_400_BAD_REQUEST)

    # Decode the base64 frame to an image
    frame_data = base64.b64decode(frame_base64)
    np_array = np.frombuffer(frame_data, np.uint8)
    frame = cv2.imdecode(np_array, cv2.IMREAD_COLOR)

    if frame is None:
        return Response({"error": "Invalid frame data"}, status=status.HTTP_400_BAD_REQUEST)

    # Retrieve the subject and lesson instances
    try:
        subject = Subject.objects.get(id=subject_id)
        lesson = Lesson.objects.get(id=lesson_id, subject=subject)
    except Subject.DoesNotExist:
        return Response({"error": "Invalid subject ID"}, status=status.HTTP_400_BAD_REQUEST)
    except Lesson.DoesNotExist:
        return Response({"error": "Invalid lesson ID for the given subject"}, status=status.HTTP_400_BAD_REQUEST)

    # Analyze the frame using the attention_status function
    analysis_result = attention_status(frame)

    # Prepare concentration data
    concentration_data = {
        "student": student_profile.user,  # Use the User instance here
        "subject": subject,
        "lesson": lesson,
        "is_concentrated": analysis_result.get("attentive"),
        "emotion": analysis_result.get("emotion"),
        "timestamp": timezone.now()
    }

    # Store the result in the Concentration table
    concentration = Concentration.objects.create(**concentration_data)

    # Return only 0 or 1 for concentration status
    return Response({
        "is_concentrated": 1 if concentration.is_concentrated else 0,
        "emotion": concentration.emotion
    }, status=status.HTTP_201_CREATED)






from keras.preprocessing.image import img_to_array
import cv2
import imutils
from keras.models import load_model
import numpy as np

# Load the models once
face_cascade = cv2.CascadeClassifier('./haarcascade_files/haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('./haarcascade_files/haarcascade_eye.xml')
emotion_classifier = load_model('./models/model_num.hdf5', compile=False)

EMOTIONS = ["angry", "disgust", "fear", "happy", "sad", "surprised", "neutral"]

# Function to process the frame
def attention_status(frame):
    emotions_map = {
        "angry": 0,
        "disgust": 0,
        "fear": 0,
        "happy": 0,
        "sad": 0,
        "surprised": 0,
        "neutral": 0
    }
    
    # Resize the frame for faster processing
    frame = imutils.resize(frame, width=400)

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the frame
    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE
    )
    
    status = {
        "attentive": False,
        "emotion": "None",
        "emotions_map": emotions_map
    }
    
    if len(faces) == 0:
        status["attentive"] = False
        status["emotion"] = "Not-Attentive (student unavailable)"
        return status

    for (x, y, w, h) in faces:
        # Extract the region of interest (ROI) of the face from grayscale image
        roi = gray[y:y + h, x:x + w]
        roi_color = frame[y:y + h, x:x + w]

        # Detect eyes in the face region
        eyes = eye_cascade.detectMultiScale(roi)
        
        # Resize and preprocess the face region for emotion classification
        roi = cv2.resize(roi, (48, 48))
        roi = roi.astype("float") / 255.0
        roi = img_to_array(roi)
        roi = np.expand_dims(roi, axis=0)

        # Predict the emotion
        preds = emotion_classifier.predict(roi)[0]
        emotion_probability = np.max(preds)
        label = EMOTIONS[preds.argmax()]
        emotions_map[label] += 1

        # Check if the person is attentive based on eye detection
        attentive = len(eyes) >= 1
        status["attentive"] = attentive
        status["emotion"] = label
        status["emotions_map"] = emotions_map

    return status





from datetime import datetime

from django.utils import timezone
from django.db import transaction
from .models import Exam, ExamQuestion, Question, MCQQuestion, TrueFalseQuestion, SortingQuestion, LongAnswerQuestion
from django.core.exceptions import ObjectDoesNotExist
import requests
# Assume AI grading function for long answer
import requests
from masarat.enums import DifficultyLevel,ChatProgress
import google.generativeai as genai

def ai_grade_long_answer(student_answer, correct_answer):
    # Configure the GenAI API key
    key = 'AIzaSyDgzTyNO0u-9F9x5p05jieJO_pEIvZZkN0'
    genai.configure(api_key=key)

    # Load the generative model
    model = genai.GenerativeModel("gemini-1.5-flash")

    # Construct the full prompt
    full_prompt = """أنت معلم خبير يمكنه مقارنة إجابة الطالب مع الإجابة النموذجية لسؤال معين. أريد منك الإجابة فقط بالنسبة المئوية لصحة الإجابة.

    مثال: الإجابة النموذجية = "التعلم تحت الإشراف: يتم التدريب على بيانات موسومة لربط المدخلات بالمخرجات (مثل اكتشاف البريد المزعج). التعلم غير الموجه: يكتشف الأنماط المخفية في البيانات غير الموسومة (مثل تقسيم العملاء). التعلم التعزيزي: يتعلم من خلال التفاعل، وزيادة المكافآت (مثل الذكاء الاصطناعي للألعاب)" إجابة الطالب = "التعلم تحت الإشراف: مثل الطالب الذي لديه مفتاح إجابة (الإجابات مقدمة). التعلم غير الموجه: مثل استكشاف مدينة جديدة بدون خريطة (لا توجد علامات أو أدلة). التعلم التعزيزي: مثل تدريب حيوان أليف باستخدام المكافآت والعقوبات (التعلم من التغذية الراجعة)." إجابتك = 90%

    الآن اتبع هذا المثال للإجابة على التالي:

    الإجابة النموذجية = """ + correct_answer + """ إجابة الطالب = """ + student_answer + """ إجابتك =
    أجب فقط بالنسبة المئوية بدون أي كلمات إضافية.
    """

    # Generate the response
    response = model.generate_content(full_prompt)
    
    if response and response.text:
        try:
            # Strip any extra whitespace and parse the response as a percentage
            result_percentage = float(response.text.replace('%', '').strip())
            return result_percentage
        except ValueError:
            print("Error: Unable to parse response as a percentage.")
            return None
    else:
        print("Error: No response received from the model.")
        return None

def grade_exam(student_id, lesson_id, chat_id, exam_type, questions):
    # Initialize counts for correct answers and total questions for difficulty levels
    beginner_correct_count = 0
    intermediate_correct_count = 0
    advanced_correct_count = 0
    challenging_correct_count = 0 

    beginner_total_count = 0
    intermediate_total_count = 0
    advanced_total_count = 0
    challenging_total_count = 0 

    with transaction.atomic():
        exam = Exam.objects.create(
            student_id=student_id,
            lesson_id=lesson_id,
            chat_id=chat_id,
            result=0,  # Placeholder, to be updated after grading
            exam_type=exam_type,
            timestamp=timezone.now(),
            passed=0,
            total_questions=0,
            percentage=0,
        )

    # Grading logic for each question
    for question_data in questions:
        question_id = question_data.get('id')
        student_answer = question_data.get('student_answer')
        
        try:
            question = Question.objects.get(id=question_id)
        except ObjectDoesNotExist:
            continue  # Skip if the question does not exist
        
        is_correct = False
        score = 0

        # Grade based on question type
        if question.question_type == 'MULTIPLE_CHOICE':
            mcq = MCQQuestion.objects.get(question=question)
            is_correct = student_answer == mcq.correct_answer
            score = 1 if is_correct else 0

        elif question.question_type == 'TRUE_FALSE':
            tf_question = TrueFalseQuestion.objects.get(question=question)
            is_correct = student_answer == tf_question.correct_answer
            score = 1 if is_correct else 0

        elif question.question_type == 'SORTING':
            sorting_question = SortingQuestion.objects.get(question=question)
            is_correct = student_answer == sorting_question.correct_order
            score = 1 if is_correct else 0

        elif question.question_type == 'LONG_ANSWER':

            long_answer_question = LongAnswerQuestion.objects.get(question=question)
            # Print time before grading
            print("Time before grading:", datetime.now())

            # Grading process
            score = ai_grade_long_answer(student_answer, long_answer_question.correct_answer)

            # Print time after grading
            print("Time after grading:", datetime.now())            # Check if the score is None (indicating an error) before proceeding
            if score is not None:
                is_correct = score >= 74.0  # Check if the AI score is at least 70%
            else:
                is_correct = False  # Set is_correct to False if there's an issue with scoring               
        # Store individual question result
        ExamQuestion.objects.create(
            exam=exam,
            question=question,
            student_answer=student_answer,
            is_true=is_correct
        )

        # Track scores and counts based on difficulty
        if question.difficulty == DifficultyLevel.BEGINNER:
            beginner_total_count += 1
            if is_correct:
                beginner_correct_count += 1
        elif question.difficulty == DifficultyLevel.INTERMEDIATE:
            intermediate_total_count += 1
            if is_correct:
                intermediate_correct_count += 1
        elif question.difficulty == DifficultyLevel.ADVANCED:
            advanced_total_count += 1
            if is_correct:
                advanced_correct_count += 1
        elif question.difficulty == DifficultyLevel.CHALLENGING:
            challenging_total_count += 1
            if is_correct:
                challenging_correct_count += 1

    # After grading all questions, determine pass/fail and update exam object
    total_correct = beginner_correct_count + intermediate_correct_count + advanced_correct_count + challenging_correct_count
    total_questions = beginner_total_count + intermediate_total_count + advanced_total_count + challenging_total_count
    score_percentage = (total_correct / total_questions) * 100 if total_questions > 0 else 0
    

    exam_passed = False





# Determine pass/fail logic based on learning phase
    if exam_type == LearningPhase.INTRO_EXAM:
        exam_passed = True  # 70% for beginner
        
        # Calculate score percentage
        total_score = beginner_correct_count + intermediate_correct_count + advanced_correct_count 
        total_questions = beginner_total_count + intermediate_total_count + advanced_total_count 
        score_percentage = (total_score / total_questions) * 100 if total_questions > 0 else 0
        
        # Categorize in UserLessonProgress based on score
        if score_percentage < 50:
            study_level = DifficultyLevel.BEGINNER
        elif 50 <= score_percentage <= 80:
            study_level = DifficultyLevel.INTERMEDIATE
        else:  # score_percentage > 80
            study_level = DifficultyLevel.ADVANCED
        
        # Create or update UserLessonProgress
        UserLessonProgress.objects.update_or_create(
            user_id=student_id,
            lesson_id=lesson_id,
            defaults={'study_level': study_level}
        )

    # Determine pass/fail logic based on learning phase
    elif exam_type == LearningPhase.EXPLANATION_EXAM:
        # Check current study level
        user_progress = UserLessonProgress.objects.filter(user_id=student_id, lesson_id=lesson_id).first()
        current_study_level = user_progress.study_level if user_progress else None
        # Determine pass/fail for each level
        beginner_passed = beginner_correct_count >= beginner_total_count * 0.5 if beginner_total_count > 0 else False
        intermediate_passed = intermediate_correct_count >= intermediate_total_count * 0.5 if intermediate_total_count > 0 else False
        advanced_passed = advanced_correct_count >= advanced_total_count * 0.5 if advanced_total_count > 0 else False
        chat = Chat.objects.filter(id = chat_id).first()

        # Determine overall result based on levels
        if current_study_level == DifficultyLevel.BEGINNER:
            if not beginner_passed:
                exam_passed = False
                # Downgrade not applicable since they are already at beginner
            else:
                exam_passed = True
        
        elif current_study_level == DifficultyLevel.INTERMEDIATE:
            if not beginner_passed:
                exam_passed = False
                # Downgrade to BEGINNER
                user_progress.study_level = DifficultyLevel.BEGINNER
                user_progress.save()
                chat.progress_state[ChatProgress.EXPLANATION_EXAM.value]["attempts"] = 0
                chat.save()            

            elif not intermediate_passed:
                exam_passed = False  # Failed in current level
            else:
                exam_passed = True

        elif current_study_level == DifficultyLevel.ADVANCED:

            if not beginner_passed:
                exam_passed = False
                # Downgrade to INTERMEDIATE
                user_progress.study_level = DifficultyLevel.INTERMEDIATE
                user_progress.save()
                chat.progress_state[ChatProgress.EXPLANATION_EXAM.value]["attempts"] = 0
                chat.save()            

            elif not intermediate_passed:
                exam_passed = False  # Failed in current level
                # Downgrade to INTERMEDIATE
                user_progress.study_level = DifficultyLevel.INTERMEDIATE
                user_progress.save()
                chat.progress_state[ChatProgress.EXPLANATION_EXAM.value]["attempts"] = 0
                chat.save()            

            elif not advanced_passed:
                exam_passed = False  # Failed in current level

            else: 
                exam_passed = True
  

    elif exam_type == LearningPhase.PREV_REVISION_EXAM:
        # Check for passing criteria in PREV_REVISION
        beginner_passed = beginner_correct_count >= beginner_total_count * 0.5 if beginner_total_count > 0 else True
        intermediate_passed = intermediate_correct_count >= intermediate_total_count * 0.5 if intermediate_total_count > 0 else True
        
        # Student fails if they fail either intermediate or beginner
        if not beginner_passed or not intermediate_passed:
            exam_passed = False
        else:
            exam_passed = True
    elif exam_type == LearningPhase.FINAL_ASSESSMENT_EXAM:
        total_correct = beginner_correct_count + intermediate_correct_count + advanced_correct_count + challenging_correct_count
        total_questions = beginner_total_count + intermediate_total_count + advanced_total_count + challenging_total_count
        exam_passed = True  
    elif exam_type == LearningPhase.CONCEPTUAL_EXAM:
        # Pass if more than 50% of beginner questions are correct
        exam_passed = beginner_correct_count > beginner_total_count * 0.5 if beginner_total_count > 0 else False
















    # Update exam results
    exam.result = total_correct
    exam.passed = exam_passed
    exam.total_questions = total_questions
    exam.percentage = score_percentage
    exam.save()

    # Return the result summary
    return {
        "exam_id": exam.id,
        "total_score": total_correct,
        "percentage":exam.percentage,
        "passed": exam_passed
    }



from chats.views import get_content_for_phase

@api_view(['GET'])
def vark_exam_content(request):
    # Define the parameters for this function call
    learning_type = ""
    difficulty_level = ""
    lesson_id= ""
    # Call the function and retrieve content
    content = get_content_for_phase(LearningPhase.VARK_EXAM.value, lesson_id, learning_type, difficulty_level)

    # Return the content as a JSON response with "content" as the key
    return Response({
        'message': (
            "دعنا نكتشف أسلوب التعلم الذي يناسبك! "
            "من خلال إجابتك على الأسئلة التالية، سنقوم بتحليل تفضيلاتك التعليمية لتحديد الأسلوب الأنسب لك."
        ),
        'id':"survey",
        'content': content
    })
