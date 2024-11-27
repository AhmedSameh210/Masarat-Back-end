import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import (
    Subject, Lesson, Topic, BaseContent, 
    VideoContent, DynamicContent,ContentType
)
from .serializers import (
    SubjectSerializer, LessonSerializer, TopicSerializer, 
    ContentSerializer, VideoContentSerializer, 
    DynamicContentSerializer
)
from django.db.models import Prefetch
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from collections import defaultdict
from users.models import StudentProfile
from masarat.enums import LearningType

# Base mixin for student authorization
class StudentAuthorizationMixin:
    permission_classes = [IsAuthenticated]

    def get_student_academic_year(self, request):
        # Get the student's academic year from the profile
        return request.user.student_profile.academic_year

# Subject List by Academic Year
# views.py
from rest_framework import generics
from .models import Subject
from .serializers import SubjectSerializer


class SubjectWithLessonsView(StudentAuthorizationMixin, generics.ListAPIView):
    serializer_class = SubjectSerializer
    def get_queryset(self):
        academic_year = self.get_student_academic_year(self.request)
        return Subject.objects.filter(academic_year=academic_year)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

# Lesson Creation
class LessonCreateView(StudentAuthorizationMixin, generics.CreateAPIView):
    serializer_class = LessonSerializer

    def perform_create(self, serializer):
        serializer.save()



# Lesson Creation
class LessonCreateView(StudentAuthorizationMixin, generics.CreateAPIView):
    serializer_class = LessonSerializer

    def perform_create(self, serializer):
        serializer.save()



# Subject Creation
class SubjectCreateView(StudentAuthorizationMixin, generics.CreateAPIView):
    serializer_class = SubjectSerializer

    def perform_create(self, serializer):
        serializer.save()



# Topic Creation
class TopicCreateView(StudentAuthorizationMixin, generics.CreateAPIView):
    serializer_class = TopicSerializer

    def perform_create(self, serializer):
        serializer.save()

# Lesson Content by Lesson
class LessonContentView(StudentAuthorizationMixin, generics.ListAPIView):
    serializer_class = ContentSerializer

    def get_queryset(self):
        lesson_id = self.kwargs['lesson_id']
        
        # Get base contents and prefetch related video or dynamic content based on type
        base_contents = BaseContent.objects.filter(lesson_id=lesson_id).prefetch_related(
            Prefetch(
                'video_content',  # Use the related_name defined in VideoContent
                queryset=VideoContent.objects.all(),
                to_attr='video_contents'  # This will be a single object due to OneToOneField
            ),
            Prefetch(
                'dynamic_content',  # Use the related_name defined in DynamicContent
                queryset=DynamicContent.objects.all(),
                to_attr='dynamic_contents'  # This will be a single object due to OneToOneField
            )
        )
        return base_contents

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        response_data = []

        for base_content in queryset:
            content_data = ContentSerializer(base_content).data
            # Append related content based on content type
            if base_content.content_type == ContentType.VIDEO:
                content_data['video_contents'] = VideoContentSerializer(
                    base_content.video_content  # Accessing single object now
                ).data if base_content.video_content else None
            elif base_content.content_type == ContentType.DYNAMIC:
                content_data['dynamic_contents'] = DynamicContentSerializer(
                    base_content.dynamic_content  # Accessing single object now
                ).data if base_content.dynamic_content else None
            response_data.append(content_data)

        return Response(response_data, status=status.HTTP_200_OK)

import os
import zipfile
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from rest_framework import generics, serializers
from .models import VideoContent, DynamicContent, ContentType, BaseContent
from .serializers import ContentSerializer

class ContentCreateView(StudentAuthorizationMixin, generics.CreateAPIView):
    serializer_class = ContentSerializer

    def perform_create(self, serializer):
        # Save the base content
        base_content = serializer.save()

        # Check content_type and handle content specifics
        content_type = self.request.data.get("content_type")

        if content_type == ContentType.VIDEO:
            file = self.request.FILES.get("file")
            if file:
                fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, "videos"))
                filename = fs.save(file.name, file)
                file_url = fs.url(os.path.join("videos", filename))

                # Create associated VideoContent
                VideoContent.objects.create(base_content=base_content, url=file_url)
            else:
                raise serializers.ValidationError({"file": "Video file is required for VIDEO content type"})

        elif content_type == ContentType.DYNAMIC:
            file = self.request.FILES.get("file")
            if file:
                # Check if the uploaded file is a ZIP file
                if not file.name.endswith('.zip'):
                    raise serializers.ValidationError({"file": "Only .zip files are accepted for DYNAMIC content type"})

                # Save the ZIP file
                fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, "web_pages"))
                zip_filename = fs.save(file.name, file)
                zip_path = fs.path(zip_filename)

                # Extract the ZIP file to a dedicated directory
                extract_dir = os.path.join(settings.MEDIA_ROOT, "web_pages", os.path.splitext(zip_filename)[0])
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)

                # Clean up the ZIP file after extraction
                os.remove(zip_path)

                # Set URL to the main page of the uploaded dynamic website
                main_page_url = fs.url(os.path.join("web_pages", os.path.splitext(zip_filename)[0], "index.html"))
                if not os.path.exists(os.path.join(extract_dir, "index.html")):
                    raise serializers.ValidationError({"file": "Main page (index.html) not found in the uploaded folder."})

                # Create associated DynamicContent
                DynamicContent.objects.create(base_content=base_content, url=main_page_url)

            else:
                raise serializers.ValidationError({"file": "ZIP file is required for DYNAMIC content type"})

        else:
            raise serializers.ValidationError({"content_type": "Invalid content type provided."})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def grade_survey(request):
    # Parse the content list from the request body
    content = request.data.get("content", [])
    if not content:
        return JsonResponse(
            {"error": "Invalid data: 'content' field is required and cannot be empty."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Map answers to learning types
    ANSWER_TO_LEARNING_TYPE = {
        "أ": LearningType.KINESTHETIC.value,
        "ب": LearningType.AUDITORY.value,
        "ج": LearningType.VISUAL.value,
        "د": LearningType.READING_WRITING.value,
    }

    # Initialize counters for learning types
    learning_type_counts = defaultdict(int)

    # Count responses for each learning type
    for question in content:
        student_answer = question.get("student_answer")
        learning_type = ANSWER_TO_LEARNING_TYPE.get(student_answer)
        if learning_type:
            learning_type_counts[learning_type] += 1

    # Determine the most frequent learning type
    best_learning_type = None
    highest_count = 0
    for l_type, count in learning_type_counts.items():
        if count > highest_count:
            highest_count = count
            best_learning_type = l_type

    if best_learning_type is None:
        best_learning_type = LearningType.VISUAL  # Default if no valid answers provided

    # Update the student's learning type in their profile
    try:
        student_profile = StudentProfile.objects.get(user=request.user)
        student_profile.learning_type = best_learning_type
        student_profile.save()
    except StudentProfile.DoesNotExist:
        return JsonResponse(
            {"error": "Student profile not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    arabic_learning_type = dict(LearningType.choices).get(best_learning_type, best_learning_type)

    result = {
        'message': f"شكرًا على إجابتك! لقد قمنا بتحليل إجاباتك، والنتائج تشير إلى أن أسلوب التعلم {arabic_learning_type} هو الأنسب لك. استعد لتجربة تعليمية مبتكرة وفعّالة!",
        "learning_type_counts": dict(learning_type_counts),  
        "best_learning_type": arabic_learning_type,  
        "content": [],
        "highest_count": highest_count,
    }

    return JsonResponse(result, status=status.HTTP_200_OK)
