from django.urls import path
from .views import QuestionViewSet, track_concentration,vark_exam_content

urlpatterns = [
    # Endpoint for creating a new question
    path('create/', QuestionViewSet.as_view({'post': 'create'}), name='question-create'),
    
    # Endpoint for retrieving questions for a specific lesson
    path('<uuid:pk>/', QuestionViewSet.as_view({'get': 'retrieve'}), name='question-retrieve'),
     # Endpoint for tracking student concentration
    path('track-concentration/', track_concentration, name='track-concentration'),
    path('vark_exam/', vark_exam_content, name='vark_exam_content'),

]
