# urls.py
from django.urls import path
from .views import answer_question, send_message,retrieve_messages_by_student_and_lesson

# Define a URL pattern for send_message manually
urlpatterns = [
    path('answer_and_audio/', answer_question, name='answer_and_generate_audio'),
    path('send_message/', send_message, name='send_message'),
    path('retrieve-messages/', retrieve_messages_by_student_and_lesson, name='retrieve_messages_by_student_and_lesson'),
    # path('generate_audio/' ,generate_audio, name='generate_audio')
]
