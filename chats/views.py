from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from .models import Chat, ChatMessage
from rest_framework.permissions import IsAuthenticated
from content_management.models import Lesson,BaseContent
from exams.models import Question, DifficultyLevel
import json
from masarat.enums import ChatProgress, LearningPhase
from users.models import LearningType , UserLessonProgress
from exams.views import grade_exam
import requests
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from exams.models import Exam
from datetime import datetime




from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from google.generativeai import GenerativeModel, configure

# Include your answer_question and read_arabic_text function implementations here:
import google.generativeai as genai
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def answer_question(request):

    question = request.data.get("question")

    key = 'AIzaSyDgzTyNO0u-9F9x5p05jieJO_pEIvZZkN0'
    genai.configure(api_key=key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    full_prompt = f"""
    أنت خبير في نظرية فيثاغورث. يمكنك الإجابة فقط عن الأسئلة المتعلقة بفيثاغورث ونظريته الشهيرة التي تنص على أن "مربع طول الوتر في مثلث قائم الزاوية يساوي مجموع مربعي طولي الضلعين الآخرين".
    السؤال: {question}
    إذا طُرحت عليك أسئلة خارج هذا النطاق، فقم بالرد بالرسالة التالية: "هذا النموذج متخصص فقط في الإجابة عن الأسئلة المتعلقة بفيثاغورث."
    """
    response = model.generate_content(full_prompt)
    return Response(
        {
            "question": question,
            "answer": response.text
            # "audio_base64": audio_base64
        },
        status=status.HTTP_200_OK
    )



from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from content_management.models import Lesson
from .models import Chat
from uuid import UUID

from uuid import UUID
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Chat, Lesson, ChatMessage
from .serializers import MessageSerializer
from datetime import datetime

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def retrieve_messages_by_student_and_lesson(request):
    """
    Retrieve all messages for a chat based on the authenticated student and lesson_id.
    If no chat exists, create one and return an empty message list.
    """
    student = request.user
    lesson_id = request.query_params.get('lesson_id')

    # Validate lesson_id
    try:
        lesson = Lesson.objects.get(id=UUID(lesson_id))
    except (Lesson.DoesNotExist, ValueError):
        return Response({"detail": "Invalid lesson_id"}, status=status.HTTP_400_BAD_REQUEST)

    # Retrieve or create chat for the student and lesson
    chat, created = Chat.objects.get_or_create(student=student, lesson=lesson)

    # If chat was newly created, it will have no messages
    if created:
        messages = []  # Empty list for a new chat
    else:
        # Retrieve all related messages for the chat
        messages = chat.messages.all()  # Assuming messages is a related model

    # Serialize the messages
    serializer = MessageSerializer(messages, many=True)
    return Response({"chat_id": chat.id, "messages": serializer.data}, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request):
    student = request.user.student_profile

    if not student:
        return Response({"error": "User not found or not authenticated."}, status=status.HTTP_401_UNAUTHORIZED)

    lesson_id = request.data.get('lesson_id')
    content = request.data.get("content", [])
    learning_type = student.learning_type

    # Retrieve the Chat instance for the current student and lesson
    chat = Chat.objects.filter(student=student.user, lesson_id=lesson_id).first()

    # Check if the chat exists
    if chat is not None:
        chat_id = chat.id  # Store the chat ID
    else:
        # Handle the case where no chat exists (you might want to create a new chat here)
        chat = Chat.objects.create(student=student.user, lesson_id=lesson_id)
        chat_id = chat.id  # Store the newly created chat ID

    progress_state = chat.progress_state or {}
    # Retrieve difficulty level from UserLessonProgress
    user_lesson_progress = UserLessonProgress.objects.filter(user=student.id, lesson_id=lesson_id).first()
    difficulty_level = user_lesson_progress.study_level if user_lesson_progress else None



    try:
            # Retrieve the lesson instance
            lesson = Lesson.objects.get(id=lesson_id)

            # Retrieve or create a Chat instance
            chat, created = Chat.objects.get_or_create(student=student.user, lesson=lesson)



            # Iterate over each element in content and save as ChatMessage
            for item in content:
                ChatMessage.objects.create(
                    chat=chat,
                    sender_type=item.get('sender_type', 'system'),
                    content=item,  # Store the entire item as JSON
                    time_stamp=timezone.now()
                )

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)







    if ChatProgress.FINAL_ASSESSMENT_EXAM.value in progress_state and progress_state[ChatProgress.FINAL_ASSESSMENT_EXAM.value]["status"] == "completed":

        # Retrieve the most recent final assessment exam for this lesson
        final_exam = Exam.objects.filter(
            student=student.user,
            lesson_id=lesson_id,
            exam_type=LearningPhase.FINAL_ASSESSMENT_EXAM.value
        ).order_by('-timestamp').first()

        if "Final_After_Improvement" in progress_state and progress_state["Final_After_Improvement"]["status"] == "none":


                    

                    # Calculate the current time in minutes once
                    now = datetime.now()
                    current_minutes = now.hour * 60 + now.minute

                    # FINAL_ASSESSMENT_EXAM
                    final_assessment_total_time = progress_state.get("Final_After_Improvement", {}).get(
                        "total_time", 0
                    )

                    # Update FINAL_ASSESSMENT_EXAM state
                    progress_state["Final_After_Improvement"] = {
                        "status": "pending",
                        "attempts": 0,
                        "starting_time": current_minutes,
                        "total_time": final_assessment_total_time
                    }
                    
                    
                    
                    # Assign the updated progress_state back to the chat instance
                    chat.progress_state = progress_state

                    # Save the chat instance to persist changes in the database
                    chat.save()
                    final_assessment_content = get_content_for_phase(
                        ChatProgress.FINAL_ASSESSMENT_EXAM.value, lesson_id, learning_type, difficulty_level
                    )



                    return Response({
                        'message': 'أحسنت، تقدم ملحوظ! لقد قطعت خطوة مهمة نحو تحسين مستواك بفهم أعمق للمفاهيم التي راجعتها. الآن، سيتم تقديم مجموعة من الأسئلة الختامية لتقييم مدى تحسنك.', 
                        'content': final_assessment_content, 
                        'lesson_id': lesson_id
                    })


        if "Final_After_Improvement" in progress_state and progress_state["Final_After_Improvement"]["status"] == "pending":


            exam_result = grade_exam(student.id,lesson_id,chat_id , ChatProgress.FINAL_ASSESSMENT_EXAM, content )


            if exam_result["passed"] == True:
                
                
                
                
                # Calculate the current time in minutes once
                now = datetime.now()
                current_minutes = now.hour * 60 + now.minute

                # Retrieve or default values for FINAL_ASSESSMENT_EXAM
                final_assessment_starting_time = progress_state.get("Final_After_Improvement", {}).get(
                    "starting_time", current_minutes
                )
                final_assessment_total_time = progress_state.get("Final_After_Improvement", {}).get(
                    "total_time", 0
                )

                # Update FINAL_ASSESSMENT_EXAM state
                progress_state["Final_After_Improvement"] = {
                    "status": "completed",
                    "attempts": 1,
                    "total_time": final_assessment_total_time + max(0, current_minutes - final_assessment_starting_time),
                    "starting_time": current_minutes
                }
                                
                final_ass_total_time = progress_state.get(ChatProgress.FINAL_ASSESSMENT_EXAM.value, {}).get("total_time", 0)

                final_ass_total_time += max(0, current_minutes - final_assessment_starting_time)

                
                # Assign the updated progress_state back to the chat instance
                chat.progress_state = progress_state

                # Save the chat instance to persist changes in the database
                chat.save()


                content = (
                    f"لقد أكملت أسئلة التقويم الختامي وحصلت على نتيجة ( {exam_result['percentage']}% ). "
                    "الآن انتهى الدرس، يمكنك مواصلة التحدث مع الذكاء الاصطناعي متى أردت لتحسين المستوى."
                )



                return Response({
                'message': (
                    f"لقد أكملت أسئلة التقويم الختامي وحصلت على نتيجة ( {exam_result['percentage']}% ). "
                    "الآن انتهى الدرس، يمكنك مواصلة التحدث مع الذكاء الاصطناعي متى أردت لتحسين المستوى."
                ),
                'content': content, 'lesson_id':lesson_id
                    })




        if final_exam:
            percentage = final_exam.percentage
            options = request.data.get('options')

            if percentage < 50:
                if options == 'أ' :
                    return Response({'Exist Succcessfully'})
                elif options == 'ب':
                    return Response({'Next Lesson Is Coming'})
                elif options =='ج' :
                    progress_state = {}
                    chat.progress_state = progress_state
                    chat.save()

            elif 50 <= percentage < 65:
                if options == 'أ'  :
                    return Response({'Exist Succcessfully'})
                elif options == 'ب' :
                    return Response({'Next Lesson Is Coming'})
                elif options =='ج' :
                    failed_topics_content = final_exam.get_failed_topics_content()


                    if not failed_topics_content:  # Checks if the list is empty
                        return Response({'message': 'لا يوجد محتوي لعرضه , لقد اجتزت جميع مفاهيم الدرس', 'content': [], 'lesson_id': lesson_id})
                    else:  # If the list is not empty
                        progress_state["Final_After_Improvement"] = {"status": "none", "attempts": 0, "starting_time": (starting_time := datetime.now().hour * 60 + datetime.now().minute) ,
                        "total_time": (lambda start, existing: existing + max(0, (datetime.now().hour * 60 + datetime.now().minute) - start))(
                            progress_state.get("Final_After_Improvement", {}).get("starting_time", (now := datetime.now()).hour * 60 + datetime.now().minute),
                            progress_state.get("Final_After_Improvement", {}).get("total_time", 0)
                        )}
                        # Assign the updated progress_state back to the chat instance
                        chat.progress_state = progress_state

                        # Save the chat instance to persist changes in the database
                        chat.save()
                        return Response({
                            'message': (
                                "قرار حكيم! "
                                "لقد اخترت تحسين نتيجتك من خلال العودة إلى الدرس. "
                                "هذا يُظهر إصرارك على التفوق. "
                                "سنقوم بإعادة عرض الأجزاء التي تحتاج إلى تعزيزها بناءً على أدائك السابق."
                            ),
                            'content': failed_topics_content,
                            'lesson_id': lesson_id
                        })


            elif 65 <= percentage < 85:
                if options =='أ' :
                    return Response({'Exist Succcessfully'})
                elif options ==  'ب':
                    return Response({'Next Lesson Is Coming'})
                elif options =='ج'  :
                    exam = Exam.objects.get(
                        student__id=student.id,
                        lesson__id=lesson_id,
                        exam_type=LearningPhase.FINAL_ASSESSMENT_EXAM.value
                    )
                    failed_topics_content = exam.get_failed_topics_content()
                


                    if not failed_topics_content:  # Checks if the list is empty
                        return Response({'message': 'لا يوجد محتوي لعرضه , لقد اجتزت جميع مفاهيم الدرس', 'content': [], 'lesson_id': lesson_id})
                    else:  # If the list is not empty
                        progress_state["Final_After_Improvement"] = {"status": "none", "attempts": 0, "starting_time": (starting_time := datetime.now().hour * 60 + datetime.now().minute) ,
                        "total_time": (lambda start, existing: existing + max(0, (datetime.now().hour * 60 + datetime.now().minute) - start))(
                            progress_state.get("Final_After_Improvement", {}).get("starting_time", (now := datetime.now()).hour * 60 + datetime.now().minute),
                            progress_state.get("Final_After_Improvement", {}).get("total_time", 0)
                        )}
                        # Assign the updated progress_state back to the chat instance
                        chat.progress_state = progress_state

                        # Save the chat instance to persist changes in the database
                        chat.save()
                        return Response({
                            'message': (
                                "قرار حكيم! "
                                "لقد اخترت تحسين نتيجتك من خلال العودة إلى الدرس. "
                                "هذا يُظهر إصرارك على التفوق. "
                                "سنقوم بإعادة عرض الأجزاء التي تحتاج إلى تعزيزها بناءً على أدائك السابق."
                            ),
                            'content': failed_topics_content,
                            'lesson_id': lesson_id
                        })






                











            elif percentage >= 85:
                if options == 'أ' :
                    return Response({'Exist Succcessfully'})
                elif options =='ب' :
                    return Response({'Next Lesson Is Coming'})
                elif options =='ج' :
                    exam = Exam.objects.get(
                        student__id=student.id,
                        lesson__id=lesson_id,
                        exam_type=LearningPhase.FINAL_ASSESSMENT_EXAM.value
                    )
                    failed_topics_content = exam.get_failed_topics_content()
                  

                    if not failed_topics_content :
                        return Response({'message': 'انت اجتزت جميع المواضيع بنجاح , لا يوجد محتوي لتحسين المستوي', 'content': failed_topics_content, 'lesson_id':lesson_id, 'is_ended': True})


                    progress_state["Final_After_Improvement"] = {"status": "none", "attempts": 0, "starting_time": (starting_time := datetime.now().hour * 60 + datetime.now().minute) ,
                    "total_time": (lambda start, existing: existing + max(0, (datetime.now().hour * 60 + datetime.now().minute) - start))(
                        progress_state.get("Final_After_Improvement", {}).get("starting_time", (now := datetime.now()).hour * 60 + datetime.now().minute),
                        progress_state.get("Final_After_Improvement", {}).get("total_time", 0)
                    )}
                    # Assign the updated progress_state back to the chat instance
                    chat.progress_state = progress_state

                    # Save the chat instance to persist changes in the database
                    chat.save()
                    return Response({
                        'message': (
                            "قرار حكيم! "
                            "لقد اخترت تحسين نتيجتك من خلال العودة إلى الدرس. "
                            "هذا يُظهر إصرارك على التفوق. "
                            "سنقوم بإعادة عرض الأجزاء التي تحتاج إلى تعزيزها بناءً على أدائك السابق."
                        ),
                        'content': failed_topics_content,
                        'lesson_id': lesson_id
                    })

                elif options == 'د' :
                    content = Question.objects.filter(
                                lesson__id=lesson_id,
                                difficulty=DifficultyLevel.CHALLENGING,
                                learning_phase=ChatProgress.FINAL_ASSESSMENT_EXAM
                                )
                    content = QuestionSerializer(content, many=True).data

                    return Response({
                        'message': (
                            "مرحبًا بالبطل المغامر! "
                            "لقد اخترت خوض سباق التحدي، وهذه خطوة رائعة تعكس شجاعتك ورغبتك في التفوق. "
                            "أسئلة التحدي التي ستوجهها الآن مصممة لتكون أكثر عمقًا وصعوبة، لكنها فرصة لإظهار قدراتك وتحقيق إنجازات جديدة. "
                            f"لقد حققت نتيجة {exam_result['percentage']}%. اضغط على 'ابدأ ' وابدأ رحلتك نحو التميز والإبداع."
                        ),
                        'content': content,
                        'lesson_id': lesson_id
                    })

                else :
                    content = request.data.get('content')
                    exam_result = grade_exam(student.id,lesson_id,chat_id , ChatProgress.FINAL_ASSESSMENT_EXAM, content )

                    return Response({
                        'message': (
                            "أحسنت يا بطل! "
                            "لقد أكملت سباق التحدي وواجهت أصعب الأسئلة بشجاعة. "
                            f"لقد حصلت على مجموع {exam_result['total_score']}%. لقد أنهيت الدرس الآن!"
                        ),
                        'action': 'Exit',
                        'lesson_id': lesson_id,
                        'content': []
                    })




    # Check if progress state is empty
    if not progress_state:
        progress_state[ChatProgress.GREETING.value] = {"status": "completed", "attempts": 1, "starting_time": (starting_time := datetime.now().hour * 60 + datetime.now().minute) ,
        "total_time": (lambda start, existing: existing + max(0, (datetime.now().hour * 60 + datetime.now().minute) - start))(
            progress_state.get(ChatProgress.INTRO_EXAM.value, {}).get("starting_time", (now := datetime.now()).hour * 60 + datetime.now().minute),
            progress_state.get(ChatProgress.GREETING.value, {}).get("total_time", 0)
        )}
        # Assign the updated progress_state back to the chat instance
        chat.progress_state = progress_state

        # Save the chat instance to persist changes in the database
        chat.save()
        return Response({'message': 'مرحبا بك في درس فيثاغورث . للمتابعه اضغط ذر التالي', 'lesson_id':lesson_id , 'content': ''})


    if len(progress_state) == 1:
        progress_state[ChatProgress.INTRO_EXAM.value] = {"status": "pending", "attempts": 0,"starting_time": (starting_time := datetime.now().hour * 60 + datetime.now().minute),  # Current time in minutes
    "total_time": progress_state.get(ChatProgress.INTRO_EXAM.value, {}).get("total_time", 0)  }

        INTRO_EXAM = get_content_for_phase(
             ChatProgress.INTRO_EXAM.value, lesson_id, learning_type, DifficultyLevel.BEGINNER.value
        )
        # Assign the updated progress_state back to the chat instance
        chat.progress_state = progress_state

        # Save the chat instance to persist changes in the database
        chat.save()
        return Response({'message': 'الآن، دعنا نتعرف على مستواك الحالي في موضوعات الدرس من خلال هذا التقويم المبدئ وذلك.•	لتحديد ما تعرفه بالفعل.•	ولاكتشاف النقاط التي تحتاج إلى تعزيز.',  'content': INTRO_EXAM})


    if ChatProgress.INTRO_EXAM.value in progress_state and progress_state[ChatProgress.INTRO_EXAM.value]["status"] == "pending":
        exam_result = grade_exam(student.id,lesson_id,chat_id , ChatProgress.INTRO_EXAM, content )
        # Retrieve difficulty level from UserLessonProgress
        user_lesson_progress = UserLessonProgress.objects.filter(user=student.id, lesson_id=lesson_id).first()
        difficulty_level = user_lesson_progress.study_level if user_lesson_progress else None


        progress_state[ChatProgress.INTRO_EXAM.value] = {"status": "completed", "attempts": 1 ,
        "total_time": (lambda start, existing: existing + max(0, (datetime.now().hour * 60 + datetime.now().minute) - start))(
            progress_state.get(ChatProgress.INTRO_EXAM.value, {}).get("starting_time", (now := datetime.now()).hour * 60 +datetime.now().minute),
            progress_state.get(ChatProgress.INTRO_EXAM.value, {}).get("total_time", 0)
        ), "starting_time": (starting_time := datetime.now().hour * 60 + datetime.now().minute)}
        progress_state[ChatProgress.INTRO_CONTENT.value] = {"status": "pending", "attempts": 0,"starting_time": (starting_time := datetime.now().hour * 60 + datetime.now().minute),  # Current time in minutes
    "total_time": progress_state.get(ChatProgress.INTRO_CONTENT.value, {}).get("total_time", 0)  }


         # Assign the updated progress_state back to the chat instance
        chat.progress_state = progress_state

        # Save the chat instance to persist changes in the database
        chat.save()



        intro_content = get_content_for_phase(
            ChatProgress.INTRO_CONTENT.value, lesson_id, learning_type, difficulty_level
        )
        return Response({'message': 'أحسنت إنجاز التقويم المبدئي!بناءً على إجاباتك، تم تحديد مستواك الحالي.الآن، سنبدأ معك بعرض تمهيد مخصص للدرس، هذا التمهيد خطوة أساسية لإعدادك لفهم أعمق خلال الدرس.', 'content': intro_content})





    if ChatProgress.INTRO_CONTENT.value in progress_state and progress_state[ChatProgress.INTRO_CONTENT.value]["status"] == "pending":
        progress_state[ChatProgress.INTRO_CONTENT.value] = {"status": "completed", "attempts": 1,"total_time": (lambda start, existing: existing + max(0, (datetime.now().hour * 60 + datetime.now().minute) - start))(
            progress_state.get(ChatProgress.INTRO_EXAM.value, {}).get("starting_time", (now := datetime.now()).hour * 60 + datetime.now().minute),
            progress_state.get(ChatProgress.INTRO_CONTENT.value, {}).get("total_time", 0)
        ), "starting_time": (starting_time := datetime.now().hour * 60 + datetime.now().minute)}

        progress_state[ChatProgress.CONCEPTUAL_EXAM.value] = {"status": "pending", "attempts": 0,"starting_time": (starting_time := datetime.now().hour * 60 + datetime.now().minute),  # Current time in minutes
    "total_time": progress_state.get(ChatProgress.CONCEPTUAL_EXAM.value, {}).get("total_time", 0)  }
        # Assign the updated progress_state back to the chat instance
        chat.progress_state = progress_state

        # Save the chat instance to persist changes in the database
        chat.save()

        CONCEPTUAL_EXAM_content = get_content_for_phase(
            ChatProgress.CONCEPTUAL_EXAM.value, lesson_id, learning_type, DifficultyLevel.BEGINNER.value,user_lesson_progress
        )
        return Response({'message': 'رائع! لقد أنهيت محتوى التمهيد بنجاح.الآن، سنعرض عليك مجموعة من الأسئلة التفاعلية المصممة لقياس مدى استيعابك للمفاهيم التي تم تقديمها.', 'content': CONCEPTUAL_EXAM_content, 'lesson_id':lesson_id})




    if ChatProgress.CONCEPTUAL_EXAM.value in progress_state and progress_state[ChatProgress.CONCEPTUAL_EXAM.value]["status"] == "pending":
        exam_result = grade_exam(student.id,lesson_id,chat_id , ChatProgress.CONCEPTUAL_EXAM, content )


        if exam_result["passed"] == True:
            # Mark CONCEPTUAL_EXAM as completed and proceed to EXPLANATION_CONTENT
            progress_state[ChatProgress.CONCEPTUAL_EXAM.value] = {"status": "completed", "attempts": 1,
        "total_time": (lambda start, existing: existing + max(0, (datetime.now().hour * 60 + datetime.now().minute) - start))(
            progress_state.get(ChatProgress.INTRO_EXAM.value, {}).get("starting_time", (now := datetime.now()).hour * 60 + datetime.now().minute),
            progress_state.get(ChatProgress.CONCEPTUAL_EXAM.value, {}).get("total_time", 0)
        ), "starting_time": (starting_time := datetime.now().hour * 60 + datetime.now().minute)}

            progress_state[ChatProgress.EXPLANATION_CONTENT.value] = {"status": "pending", "attempts": 0,"starting_time": (starting_time := datetime.now().hour * 60 + datetime.now().minute),  # Current time in minutes
    "total_time": progress_state.get(ChatProgress.EXPLANATION_CONTENT.value, {}).get("total_time", 0)  }
            # Assign the updated progress_state back to the chat instance
            chat.progress_state = progress_state

            # Save the chat instance to persist changes in the database
            chat.save()
            explanation_content_after_exam = get_content_for_phase(
                ChatProgress.EXPLANATION_CONTENT.value, lesson_id, learning_type, difficulty_level
            )
            return Response({
                'message': 'عمل رائع! بناءً على إجاباتك وأسلوب التعلم المفضل لديك، سنعرض الآن محتوى شرح الدرس.',
                'content': explanation_content_after_exam, 'lesson_id':lesson_id
            })
        else:
            # If exam is failed, mark CONCEPTUAL_EXAM as "failed"
            progress_state[ChatProgress.CONCEPTUAL_EXAM.value] = {"status": "failed", "attempts": progress_state[ChatProgress.CONCEPTUAL_EXAM.value].get("attempts", 0) + 1,
        "total_time": (lambda start, existing: existing + max(0, (datetime.now().hour * 60 + datetime.now().minute) - start))(
            progress_state.get(ChatProgress.CONCEPTUAL_EXAM.value, {}).get("starting_time", (now := datetime.now()).hour * 60 + datetime.now().minute),
            progress_state.get(ChatProgress.CONCEPTUAL_EXAM.value, {}).get("total_time", 0)
        ), "starting_time": (starting_time := datetime.now().hour * 60 + datetime.now().minute) }
            # Assign the updated progress_state back to the chat instance
            chat.progress_state = progress_state

            # Save the chat instance to persist changes in the database
            chat.save()


    # Additional outer check for handling failed CONCEPTUAL_EXAM
    if progress_state.get(ChatProgress.CONCEPTUAL_EXAM.value, {}).get("status") == "failed":
        # Reset INTRO_CONTENT to allow the student to revisit it
        progress_state[ChatProgress.INTRO_CONTENT.value] = {"status": "pending", "attempts": 0,"starting_time": (starting_time := datetime.now().hour * 60 + datetime.now().minute),  # Current time in minutes
    "total_time": progress_state.get(ChatProgress.INTRO_CONTENT.value, {}).get("total_time", 0)  }
        # Assign the updated progress_state back to the chat instance
        chat.progress_state = progress_state

        # Save the chat instance to persist changes in the database
        chat.save()
        intro_content = get_content_for_phase(
            ChatProgress.INTRO_CONTENT.value, lesson_id, learning_type, difficulty_level
        )
        return Response({
            'message': (
                "يبدو أن إجابتك على أسئلة التقويم الخاصة بالتمهيد لم تكن صحيحة. "
                "لا عليك. سوف نقوم بإعادة عرض التمهيد مرة أخرى."
            ),
            'content': intro_content,
            'lesson_id': lesson_id
        })









    if ChatProgress.EXPLANATION_CONTENT.value in progress_state and progress_state[ChatProgress.EXPLANATION_CONTENT.value]["status"] == "pending":
        # Mark EXPLANATION_CONTENT as completed
        progress_state[ChatProgress.EXPLANATION_CONTENT.value] = {"status": "completed", "attempts":1,
        "total_time": (lambda start, existing: existing + max(0, (datetime.now().hour * 60 + datetime.now().minute) - start))(
            progress_state.get(ChatProgress.INTRO_EXAM.value, {}).get("starting_time", (now := datetime.now()).hour * 60 +datetime.now().minute),
            progress_state.get(ChatProgress.EXPLANATION_CONTENT.value, {}).get("total_time", 0)
        ), "starting_time": (starting_time := datetime.now().hour * 60 + datetime.now().minute)}
        # Assign the updated progress_state back to the chat instance
        chat.progress_state = progress_state

        # Save the chat instance to persist changes in the database
        chat.save()

        # Otherwise, initialize EXPLANATION_EXAM phase as pending
        progress_state[ChatProgress.EXPLANATION_EXAM.value] = {"status": "pending", "attempts": progress_state.get(ChatProgress.EXPLANATION_EXAM.value, {}).get("attempts", 0),"starting_time": (starting_time := datetime.now().hour * 60 + datetime.now().minute),  # Current time in minutes
    "total_time": progress_state.get(ChatProgress.EXPLANATION_EXAM.value, {}).get("total_time", 0)  }
        # Assign the updated progress_state back to the chat instance
        chat.progress_state = progress_state

        # Save the chat instance to persist changes in the database
        chat.save()
        explanation_exam_content = get_content_for_phase(
            ChatProgress.EXPLANATION_EXAM.value, lesson_id, learning_type, difficulty_level
        )
        return Response({'message': 'أحسنت! لقد أكملت محتوى الشرح بنجاح. حان الآن الوقت لتطبيق ما تعلمته والإجابة على مجموعة من الأسئلة التفاعلية.', 'content': explanation_exam_content, 'lesson_id':lesson_id})





    if (ChatProgress.EXPLANATION_EXAM.value in progress_state and
        progress_state[ChatProgress.EXPLANATION_EXAM.value]["status"] == "pending"):
        # Check current study level
        user_progress = UserLessonProgress.objects.filter(user_id=student.id, lesson_id=lesson_id).first()
        current_study_level = user_progress.study_level if user_progress else None
        explanation_exam_result = grade_exam(student.id,lesson_id,chat_id , ChatProgress.EXPLANATION_EXAM, content )
        user_progress2 = UserLessonProgress.objects.filter(user_id=student.id, lesson_id=lesson_id).first()
        current_study_level2 = user_progress2.study_level if user_progress else None


        downgraded = current_study_level2 != current_study_level
        # Case 1: Explanation Exam Passed
        if explanation_exam_result["passed"] == True:

            # Compute current time once
            now = datetime.now()
            current_minutes = now.hour * 60 + now.minute
            starting_time = current_minutes


            # Update EXPLANATION_EXAM
            explanation_exam_start_time = progress_state.get(ChatProgress.EXPLANATION_EXAM.value, {}).get("starting_time", starting_time)
            existing_total_time = progress_state.get(ChatProgress.EXPLANATION_EXAM.value, {}).get("total_time", 0)


            progress_state[ChatProgress.EXPLANATION_EXAM.value] = {
                "status": "completed",
                "attempts": progress_state.get(ChatProgress.EXPLANATION_EXAM.value, {}).get("attempts", 0) + 1,
                "total_time": existing_total_time + max(0, current_minutes - explanation_exam_start_time),
                "starting_time": starting_time
            }

            # Update PREVIOUS_CONTENT_CONTENT
            progress_state[ChatProgress.PREVIOUS_CONTENT_CONTENT.value] = {
                "status": "pending",
                "attempts": 0,
                "starting_time": starting_time,
                "total_time": progress_state.get(ChatProgress.PREVIOUS_CONTENT_CONTENT.value, {}).get("total_time", 0)
            }
            
            
            
            chat.progress_state = progress_state

            # Save the chat instance to persist changes in the database
            chat.save()

            intro_exam = Exam.objects.filter(
            student=student.user,
            lesson_id=lesson_id,
            exam_type=LearningPhase.INTRO_EXAM.value
            ).order_by('-timestamp').first()


            previous_content =intro_exam.get_failed_topics_for_previous_content()
            if not previous_content:  # Checks if the list is empty
                return Response({'message': 'لقد اجتزت كل مفاهيم الدرس , لا يوجد محتوي لتحسين مستواك', 'content': [], 'lesson_id': lesson_id})
            else:  # If the list is not empty
                return Response({'message': 'عمل رائع! لقد أكملت الأسئلة بنجاح. سنعرض لك الآن محتوى مخصصًا لهذه المفاهيم.', 'content': previous_content, 'lesson_id': lesson_id})

        # Case 2: Explanation Exam Failed - Flag as Failed
        else:
            # Retrieve difficulty level from UserLessonProgress
            user_lesson_progress = UserLessonProgress.objects.filter(user=student.id, lesson_id=lesson_id).first()
            difficulty_level = user_lesson_progress.study_level if user_lesson_progress else None
            if downgraded:
                attempts = progress_state[ChatProgress.EXPLANATION_EXAM.value].get("attempts", 0)
            else :
                attempts = progress_state[ChatProgress.EXPLANATION_EXAM.value].get("attempts", 0)+1


            # Compute current time once
            now = datetime.now()
            current_minutes = now.hour * 60 + now.minute
            starting_time = current_minutes

            # Get existing total time and starting time
            starting_time_explanation = progress_state.get(ChatProgress.EXPLANATION_EXAM.value, {}).get("starting_time", starting_time)
            existing_total_time_explanation = progress_state.get(ChatProgress.EXPLANATION_EXAM.value, {}).get("total_time", 0)

            # Update EXPLANATION_EXAM state
            progress_state[ChatProgress.EXPLANATION_EXAM.value] = {
                "status": "failed",
                "attempts": attempts,  # `attempts` variable assumed to be defined elsewhere
                "total_time": existing_total_time_explanation + max(0, current_minutes - starting_time_explanation),
                "starting_time": starting_time
            }


            
            # Assign the updated progress_state back to the chat instance
            chat.progress_state = progress_state

            # Save the chat instance to persist changes in the database
            chat.save()

    # Separate Condition Block for Handling Failed EXPLANATION_EXAM
    if ChatProgress.EXPLANATION_EXAM.value in progress_state and progress_state[ChatProgress.EXPLANATION_EXAM.value]["status"] == "failed":
        attempts = progress_state[ChatProgress.EXPLANATION_EXAM.value]["attempts"]

        # Learning Type Handling based on failure attempts
        if learning_type == LearningType.VISUAL:
            # Visual → Kinesthetic → Reading/Writing → Auditory
            if downgraded:
                content = get_content_for_phase(ChatProgress.EXPLANATION_CONTENT.value, lesson_id, LearningType.VISUAL, difficulty_level)
            elif attempts == 1:
                content = get_content_for_phase(ChatProgress.EXPLANATION_CONTENT.value, lesson_id, LearningType.KINESTHETIC, difficulty_level)
            elif attempts == 2:
                content = get_content_for_phase(ChatProgress.EXPLANATION_CONTENT.value, lesson_id, LearningType.READING_WRITING, difficulty_level)
            elif attempts == 3:
                content = get_content_for_phase(ChatProgress.EXPLANATION_CONTENT.value, lesson_id, LearningType.AUDITORY, difficulty_level)

        elif learning_type == LearningType.AUDITORY:
            # Auditory → Reading/Writing → Kinesthetic → Visual

            if downgraded:
                content = get_content_for_phase(ChatProgress.EXPLANATION_CONTENT.value, lesson_id, LearningType.AUDITORY, difficulty_level)
            elif attempts == 1:
                content = get_content_for_phase(ChatProgress.EXPLANATION_CONTENT.value, lesson_id, LearningType.READING_WRITING, difficulty_level)
            elif attempts == 2:
                content = get_content_for_phase(ChatProgress.EXPLANATION_CONTENT.value, lesson_id, LearningType.KINESTHETIC, difficulty_level)
            elif attempts == 3:
                content = get_content_for_phase(ChatProgress.EXPLANATION_CONTENT.value, lesson_id, LearningType.VISUAL, difficulty_level)

        elif learning_type == LearningType.KINESTHETIC:
            # Kinesthetic → Visual → Reading/Writing → Auditory
            if downgraded:
                content = get_content_for_phase(ChatProgress.EXPLANATION_CONTENT.value, lesson_id, LearningType.KINESTHETIC, difficulty_level)
            elif attempts == 1:
                content = get_content_for_phase(ChatProgress.EXPLANATION_CONTENT.value, lesson_id, LearningType.VISUAL, difficulty_level)
            elif attempts == 2:
                content = get_content_for_phase(ChatProgress.EXPLANATION_CONTENT.value, lesson_id, LearningType.READING_WRITING, difficulty_level)
            elif attempts == 3:
                content = get_content_for_phase(ChatProgress.EXPLANATION_CONTENT.value, lesson_id, LearningType.AUDITORY, difficulty_level)

        elif learning_type == LearningType.READING_WRITING:
            # Reading/Writing → Visual → Kinesthetic → Auditory
            if downgraded:
                content = get_content_for_phase(ChatProgress.EXPLANATION_CONTENT.value, lesson_id, LearningType.READING_WRITING, difficulty_level)
            elif attempts == 1:
                content = get_content_for_phase(ChatProgress.EXPLANATION_CONTENT.value, lesson_id, LearningType.VISUAL, difficulty_level)
            elif attempts == 2:
                content = get_content_for_phase(ChatProgress.EXPLANATION_CONTENT.value, lesson_id, LearningType.KINESTHETIC, difficulty_level)
            elif attempts == 3:
                content = get_content_for_phase(ChatProgress.EXPLANATION_CONTENT.value, lesson_id, LearningType.AUDITORY, difficulty_level)

        # Difficulty Level Reduction if all learning types are exhausted
        if attempts >= 4:
            beginner_flag = user_lesson_progress.study_level == DifficultyLevel.BEGINNER
            if difficulty_level == DifficultyLevel.ADVANCED:
                difficulty_level = DifficultyLevel.INTERMEDIATE
                user_lesson_progress.study_level = difficulty_level  # set your new level here
                user_lesson_progress.save()
            elif difficulty_level == DifficultyLevel.INTERMEDIATE:
                difficulty_level = DifficultyLevel.BEGINNER
                user_lesson_progress.study_level = difficulty_level  # set your new level here
                user_lesson_progress.save()
            progress_state[ChatProgress.EXPLANATION_EXAM.value]["attempts"] = 0


     
     

            # Compute current time once
            now = datetime.now()
            current_minutes = now.hour * 60 + now.minute
            starting_time = current_minutes

            # Get existing total time for EXPLANATION_CONTENT
            existing_total_time = progress_state.get(ChatProgress.EXPLANATION_CONTENT.value, {}).get("total_time", 0)

            # Update EXPLANATION_CONTENT state
            progress_state[ChatProgress.EXPLANATION_CONTENT.value] = {
                "status": "pending",
                "attempts": 0,
                "starting_time": starting_time,  # Current time in minutes
                "total_time": existing_total_time
            }




            # Assign the updated progress_state back to the chat instance
            chat.progress_state = progress_state

            # Save the chat instance to persist changes in the database
            chat.save()
            content = get_content_for_phase(ChatProgress.EXPLANATION_CONTENT.value, lesson_id, learning_type, difficulty_level)
            if not beginner_flag :
                return Response({
                    'message': 'لا تقلق، سنساعدك على الفهم بشكل أفضل ! لاحظنا أنك واجهت صعوبة في الإجابة على بعض الأسئلة. سنعيد تقديم المحتوى بطريقة مختلفة تناسب أسلوب تعلمك بشكل أفضل.',
                    'content': content, 'lesson_id':lesson_id
                })
  
        # Compute current time once
        now = datetime.now()
        current_minutes = now.hour * 60 + now.minute

        # Get existing total time for EXPLANATION_CONTENT
        existing_total_time = progress_state.get(ChatProgress.EXPLANATION_CONTENT.value, {}).get("total_time", 0)

        # Update or initialize EXPLANATION_CONTENT state
        progress_state[ChatProgress.EXPLANATION_CONTENT.value] = {
            "status": "pending",
            "attempts": 0,
            "starting_time": current_minutes,  # Current time in minutes
            "total_time": existing_total_time
        }


        chat.progress_state = progress_state
        chat.save()
        # Provide fallback content based on current attempt count
        if not downgraded:
            return Response({
                'message': 'نتائجك تهمنا، ونسعى لتقديم الأفضل! لاحظنا أنك لم تحقق النتائج المرجوة باستخدام أسلوب التعلم الحالي. سنقوم بعرض المحتوى بطريقة مختلفة تعتمد على أسلوب تعلم آخر قد يكون أكثر توافقًا مع احتياجاتك.',
                'content': content, 
                'lesson_id': lesson_id
            })
        else:
            return Response({
                'message': 'لا تقلق، سنساعدك على الفهم بشكل أفضل! لاحظنا أنك واجهت صعوبة في الإجابة على بعض الأسئلة. سنعيد تقديم المحتوى بطريقة مختلفة تناسب أسلوب تعلمك بشكل أفضل.',
                'content': content, 
                'lesson_id': lesson_id
            })





    if ChatProgress.PREVIOUS_CONTENT_CONTENT.value in progress_state and progress_state[ChatProgress.PREVIOUS_CONTENT_CONTENT.value]["status"] == "pending":
        

        # Compute current time once
        now = datetime.now()
        current_minutes = now.hour * 60 + now.minute

        # Get starting time for INTRO_EXAM or default to the current time
        previous_content_starting_time = progress_state.get(ChatProgress.PREVIOUS_CONTENT_CONTENT.value, {}).get("starting_time", current_minutes)

        # Get existing total time for PREVIOUS_CONTENT_CONTENT or default to 0
        existing_total_time = progress_state.get(ChatProgress.PREVIOUS_CONTENT_CONTENT.value, {}).get("total_time", 0)

        # Update or initialize PREVIOUS_CONTENT_CONTENT state
        progress_state[ChatProgress.PREVIOUS_CONTENT_CONTENT.value] = {
            "status": "completed",
            "attempts": 1,
            "total_time": existing_total_time + max(0, current_minutes - previous_content_starting_time),
            "starting_time": current_minutes
        }

        # Assign the updated progress_state back to the chat instance
        chat.progress_state = progress_state

        # Save the chat instance to persist changes in the database
        chat.save()
        if ChatProgress.PREV_REVISION_EXAM.value in progress_state and progress_state[ChatProgress.PREV_REVISION_EXAM.value]["status"] == "failed":
            # Skip setting PREV_REVISION_EXAM to pending again if it's already failed
            pass
        else:


            # Compute current time once
            now = datetime.now()
            current_minutes = now.hour * 60 + now.minute

            # Get existing total time for PREV_REVISION_EXAM or default to 0
            existing_total_time = progress_state.get(ChatProgress.PREV_REVISION_EXAM.value, {}).get("total_time", 0)

            # Update or initialize PREV_REVISION_EXAM state
            progress_state[ChatProgress.PREV_REVISION_EXAM.value] = {
                "status": "pending",
                "attempts": 0,
                "starting_time": current_minutes,  # Current time in minutes
                "total_time": existing_total_time
            }
            
            
            # Assign the updated progress_state back to the chat instance
            chat.progress_state = progress_state

            # Save the chat instance to persist changes in the database
            chat.save()
        intro_exam = Exam.objects.filter(
                    student=student.user,
                    lesson_id=lesson_id,
                    exam_type=LearningPhase.INTRO_EXAM.value
                    ).order_by('-timestamp').first()

        prev_revision_exam = intro_exam.get_failed_topics_for_previous_exam()
        return Response({'message': 'ممتاز! لقد أكملت مراجعة المفاهيم الأساسية بنجاح. للتأكد من استيعابك لهذه المفاهيم، سنعرض عليك الآن مجموعة من الأسئلة.', 'content': prev_revision_exam, 'lesson_id':lesson_id})




    if ChatProgress.PREV_REVISION_EXAM.value in progress_state and progress_state[ChatProgress.PREV_REVISION_EXAM.value]["status"] in ["pending", "failed"] :


        prev_revision_exam_result = grade_exam(student.id,lesson_id,chat_id , ChatProgress.PREV_REVISION_EXAM, content )


        if prev_revision_exam_result["passed"] == True or progress_state[ChatProgress.PREV_REVISION_EXAM.value].get("attempts", 0) >= 2:


            # Compute current time once
            now = datetime.now()
            current_minutes = now.hour * 60 + now.minute

            # Get starting time for INTRO_EXAM or default to the current time
            prev_revision_starting_time = progress_state.get(ChatProgress.PREV_REVISION_EXAM.value, {}).get("starting_time", current_minutes)

            # Get existing total time for PREV_REVISION_EXAM or default to 0
            prev_revision_total_time = progress_state.get(ChatProgress.PREV_REVISION_EXAM.value, {}).get("total_time", 0)

            # Calculate total time for PREV_REVISION_EXAM
            prev_revision_total_time += max(0, current_minutes - prev_revision_starting_time)

            # Update or initialize PREV_REVISION_EXAM state
            progress_state[ChatProgress.PREV_REVISION_EXAM.value] = {
                "status": "completed",
                "attempts": 3,
                "total_time": prev_revision_total_time,
                "starting_time": current_minutes
            }

            # Get existing total time for PRACTICE_VIDEOS_CONTENT or default to 0
            practice_videos_total_time = progress_state.get(ChatProgress.PRACTICE_VIDEOS_CONTENT.value, {}).get("total_time", 0)

            # Update or initialize PRACTICE_VIDEOS_CONTENT state
            progress_state[ChatProgress.PRACTICE_VIDEOS_CONTENT.value] = {
                "status": "pending",
                "attempts": 0,
                "starting_time": current_minutes,  # Current time in minutes
                "total_time": practice_videos_total_time
            }  
            
            
            
            # Assign the updated progress_state back to the chat instance
            chat.progress_state = progress_state

            # Save the chat instance to persist changes in the database
            chat.save()
            practice_videos_content = get_content_for_phase(
                ChatProgress.PRACTICE_VIDEOS_CONTENT.value, lesson_id, learning_type, difficulty_level
            )
            return Response({'message': 'رائع! لقد أنهيت تقييم المفاهيم الأساسية بنجاح. الآن، سنعرض عليك مثالاً عمليًا يُظهر استخدام المفاهيم التي تعلمتها في حل مشكلة من واقع الحياة.', 'content': practice_videos_content, 'lesson_id':lesson_id})
        else :
            
            
            # Compute current time once
            now = datetime.now()
            current_minutes = now.hour * 60 + now.minute

            # Update attempts for PREV_REVISION_EXAM
            prev_revision_attempts = progress_state.get(ChatProgress.PREV_REVISION_EXAM.value, {}).get("attempts", 0) + 1

            # Get starting time for PREV_REVISION_EXAM or default to the current time
            prev_revision_starting_time = progress_state.get(ChatProgress.PREV_REVISION_EXAM.value, {}).get("starting_time", current_minutes)

            # Get existing total time for PREV_REVISION_EXAM or default to 0
            prev_revision_total_time = progress_state.get(ChatProgress.PREV_REVISION_EXAM.value, {}).get("total_time", 0)

            # Calculate new total time for PREV_REVISION_EXAM
            prev_revision_total_time += max(0, current_minutes - prev_revision_starting_time)

            # Update PREV_REVISION_EXAM state
            progress_state[ChatProgress.PREV_REVISION_EXAM.value] = {
                "status": "failed",
                "attempts": prev_revision_attempts,
                "total_time": prev_revision_total_time,
                "starting_time": current_minutes
            }

            # Get existing total time for PREVIOUS_CONTENT_CONTENT or default to 0
            previous_content_total_time = progress_state.get(ChatProgress.PREVIOUS_CONTENT_CONTENT.value, {}).get("total_time", 0)

            # Update PREVIOUS_CONTENT_CONTENT state
            progress_state[ChatProgress.PREVIOUS_CONTENT_CONTENT.value] = {
                "status": "pending",
                "attempts": 0,
                "starting_time": current_minutes,  # Current time in minutes
                "total_time": previous_content_total_time
            }
            
            
            
            # Assign the updated progress_state back to the chat instance
            chat.progress_state = progress_state

            # Save the chat instance to persist changes in the database
            chat.save()
            intro_exam = Exam.objects.filter(
            student=student.user,
            lesson_id=lesson_id,
            exam_type=LearningPhase.INTRO_EXAM.value
            ).order_by('-timestamp').first()


            previous_content =intro_exam.get_failed_topics_for_previous_content()
            return Response({
                'message': (
                    "يبدو أن إجابتك على أسئلة التقويم الخاصة بالمفاهيم الأساسية لم تكن صحيحة. "
                    "لا بأس. سوف نقوم بإعادة عرض المفاهيم الأساسية مرة أخرى."
                ),
                'content': previous_content,
                'lesson_id': lesson_id
            })




    if ChatProgress.PRACTICE_VIDEOS_CONTENT.value in progress_state and progress_state[ChatProgress.PRACTICE_VIDEOS_CONTENT.value]["status"] == "pending":



        # Calculate the current time in minutes once
        now = datetime.now()
        current_minutes = now.hour * 60 + now.minute

        # PRACTICE_VIDEOS_CONTENT
        practice_videos_starting_time = progress_state.get(ChatProgress.PRACTICE_VIDEOS_CONTENT.value, {}).get(
            "starting_time", current_minutes
        )
        practice_videos_total_time = progress_state.get(ChatProgress.PRACTICE_VIDEOS_CONTENT.value, {}).get(
            "total_time", 0
        )

        # Calculate new total time for PRACTICE_VIDEOS_CONTENT
        practice_videos_total_time += max(0, current_minutes - practice_videos_starting_time)

        # Update PRACTICE_VIDEOS_CONTENT state
        progress_state[ChatProgress.PRACTICE_VIDEOS_CONTENT.value] = {
            "status": "completed",
            "attempts": 1,
            "total_time": practice_videos_total_time,
            "starting_time": current_minutes
        }

        # EXERCISES_CONTENT
        exercises_total_time = progress_state.get(ChatProgress.EXERCISES_CONTENT.value, {}).get("total_time", 0)

        # Update EXERCISES_CONTENT state
        progress_state[ChatProgress.EXERCISES_CONTENT.value] = {
            "status": "pending",
            "attempts": 0,
            "starting_time": current_minutes,
            "total_time": exercises_total_time
        }
                
        
        
        
        
        
        # Assign the updated progress_state back to the chat instance
        chat.progress_state = progress_state

        # Save the chat instance to persist changes in the database
        chat.save()
        exercises_exam_content = get_content_for_phase(
            ChatProgress.EXERCISES_CONTENT.value, lesson_id, learning_type, difficulty_level
        )
        return Response({'message': 'رائع جدًا! لقد أنهيت التطبيقات والأمثلة بنجاح.الآن، حان وقت التدرب على المفاهيم التي تعلمتها من خلال نشاط تفاعلي مصمم لتعزيز استيعابك. ', 'content': exercises_exam_content, 'lesson_id':lesson_id})



    if ChatProgress.EXERCISES_CONTENT.value in progress_state and progress_state[ChatProgress.EXERCISES_CONTENT.value]["status"] == "pending":
            # Proceed directly to set FINAL_ASSESSMENT_EXAM as pending


        # Calculate the current time in minutes once
        now = datetime.now()
        current_minutes = now.hour * 60 + now.minute

        # EXERCISES_CONTENT
        exercises_starting_time = progress_state.get(ChatProgress.EXERCISES_CONTENT.value, {}).get(
            "starting_time", current_minutes
        )
        exercises_total_time = progress_state.get(ChatProgress.EXERCISES_CONTENT.value, {}).get(
            "total_time", 0
        )

        # Update EXERCISES_CONTENT state
        progress_state[ChatProgress.EXERCISES_CONTENT.value] = {
            "status": "completed",
            "attempts": 1,
            "total_time": exercises_total_time + max(0, current_minutes - exercises_starting_time),
            "starting_time": current_minutes
        }

        # FINAL_ASSESSMENT_EXAM
        final_assessment_total_time = progress_state.get(ChatProgress.FINAL_ASSESSMENT_EXAM.value, {}).get(
            "total_time", 0
        )

        # Update FINAL_ASSESSMENT_EXAM state
        progress_state[ChatProgress.FINAL_ASSESSMENT_EXAM.value] = {
            "status": "pending",
            "attempts": 0,
            "starting_time": current_minutes,
            "total_time": final_assessment_total_time
        }
        
        
        
        # Assign the updated progress_state back to the chat instance
        chat.progress_state = progress_state

        # Save the chat instance to persist changes in the database
        chat.save()
        final_assessment_content = get_content_for_phase(
            ChatProgress.FINAL_ASSESSMENT_EXAM.value, lesson_id, learning_type, difficulty_level
        )

        return Response({'message': 'أحسنت العمل! لقد أكملت التدريبات بنجاح.الآن، سننتقل إلى الخطوة الأخيرة في هذا الدرس. من خلال أسئلة التقويم الختامي.', 'content': final_assessment_content, 'lesson_id':lesson_id})





    if ChatProgress.FINAL_ASSESSMENT_EXAM.value in progress_state and progress_state[ChatProgress.FINAL_ASSESSMENT_EXAM.value]["status"] == "pending":

            exam_result = grade_exam(student.id,lesson_id,chat_id , ChatProgress.FINAL_ASSESSMENT_EXAM, content )


            if exam_result["passed"] == True:
                
                
                
                
                # Calculate the current time in minutes once
                now = datetime.now()
                current_minutes = now.hour * 60 + now.minute

                # Retrieve or default values for FINAL_ASSESSMENT_EXAM
                final_assessment_starting_time = progress_state.get(ChatProgress.FINAL_ASSESSMENT_EXAM.value, {}).get(
                    "starting_time", current_minutes
                )
                final_assessment_total_time = progress_state.get(ChatProgress.FINAL_ASSESSMENT_EXAM.value, {}).get(
                    "total_time", 0
                )

                # Update FINAL_ASSESSMENT_EXAM state
                progress_state[ChatProgress.FINAL_ASSESSMENT_EXAM.value] = {
                    "status": "completed",
                    "attempts": 1,
                    "total_time": final_assessment_total_time + max(0, current_minutes - final_assessment_starting_time),
                    "starting_time": current_minutes
                }
                                
                
                
                # Assign the updated progress_state back to the chat instance
                chat.progress_state = progress_state

                # Save the chat instance to persist changes in the database
                chat.save()

                if exam_result['percentage'] < 50:
                    options = [
                        {"أ":"خروج"},
                        {"ب":"الدرس التالي"},
                       { "ج" :"اعاده الدرس"}
                    ]
                    content = (
                        "لا بأس، يمكنك تحسين مستواك! لا تقلق، يمكننا المحاولة مجددًا! "
                        f"لقد انتهيت من أسئلة التقويم الختامي، بمجموع ( {exam_result['percentage']}% )، مما يشير إلى أنك لم تحقق درجة النجاح المطلوبة. "
                        "يبدو أنك واجهت بعض التحديات في فهم الدرس. ما الذي يمكنك القيام به الآن؟\n"
                        f"أ) {options[0]}\n"
                        f"ب) {options[1]}\n"
                        f"جـ) {options[2]}"
                    )


                    return Response({
                    'message': '   ---   ',
                    'content': content, 'lesson_id':lesson_id, "options" : options,"grade" : exam_result['percentage']
                })

                elif 50 <= exam_result['percentage'] < 65:
                    options = [
                        {"أ":"خروج"},
                        {"ب":"الدرس التالي"},
                        {"ج" :"تحسين المستوي"}
                    ]
                    content = (
                        "أداء جيد، لكن يمكننا الوصول للأفضل! "
                        f"لقد أكملت أسئلة التقويم الختامي وحصلت على نتيجة ( {exam_result['percentage']}% )، مما يعني أنك اجتزت الدرس بتقدير 'جيد'. "
                        "نقدر جهدك والعمل الذي بذلته، ولكننا نعتقد أنه بإمكانك تحقيق مستوى أعلى. كيف يمكننا مساعدتك؟\n"
                        f"أ) {options[0]}\n"
                        f"ب) {options[1]}\n"
                        f"جـ) {options[2]}"
                    )


                    return Response({
                    'message': '   ---   ',
                    'content': content, 'lesson_id':lesson_id, "options" : options,"grade" : exam_result['percentage']
                })

                elif 65 <= exam_result['percentage'] < 85:
                    options = [
                        {"أ":"خروج"},
                        {"ب":"الدرس التالي"},
                        {"ج" :"تحسين المستوي"}
                    ]
                    content = (
                        "عمل رائع! ولكن هناك مجال للمزيد من التميز! "
                        f"لقد أكملت أسئلة التقويم الختامي وحصلت على نتيجة ( {exam_result['percentage']}% ). "
                        "هذا يُظهر أنك بذلت مجهودًا كبيرًا، وحققت تقدير 'جيد جدًا'. نهنئك على هذا الإنجاز المميز!\n"
                        "كيف نساعدك لتحقيق المزيد؟\n"
                        f"أ) {options[0]}\n"
                        f"ب) {options[1]}\n"
                        f"جـ) {options[2]}\n"
                    )


                    return Response({
                    'message': '   ---   ',
                    'content': content, 'lesson_id':lesson_id, "options" : options,"grade" : exam_result['percentage']
                })
                else:  # exam_result['percentage'] > 85
                    options = [
                        {"أ":"خروج"},
                        {"ب":"الدرس التالي"},
                        {"ج" :"تحسين المستوي"},
                        {"د" :"اسأله التحدي"}
                    ]


                    content = (
                        "أنت نجم متألق! "
                        f"تهانينا! لقد أكملت أسئلة التقويم الختامي وحققت نتيجة ( {exam_result['percentage']}% ) مما يمنحك تقدير 'ممتاز'. "
                        "هذا دليل على مجهودك الرائع وفهمك العميق للدرس. نحن فخورون جدًا بإنجازك!\n"
                        "اختر ما بين الخيارات التالية لتحقيق المزيد:\n"
                        f"أ) {options[0]}\n"
                        f"ب) {options[1]}\n"
                        f"جـ) {options[2]}\n"
                        f"د) {options[3]}"
                    )


                    return Response({
                    'message': '   ---   ',
                    'content': content, 'lesson_id':lesson_id, "options" : options,"grade" : exam_result['percentage']
                })





    return Response({"Error Message" : "No Case Found !!!!!!!!!!!!!!!!"})








from content_management.serializers import ContentSerializer
from exams.serializers import QuestionSerializer  # Import the QuestionSerializer

def get_content_for_phase(progress_phase, lesson_id, learning_type, difficulty_level, user_lesson_progress=None):
    """
    Retrieves content based on progress phase, learning type, and difficulty level.
    Adds audio_base64 attribute to content descriptions, question texts, and merged question/choice audio.
    """
    content = ""

    if progress_phase.endswith('CONTENT'):
        # Filter BaseContent by lesson, learning phase, learning type, and difficulty level
        content_queryset = BaseContent.objects.filter(
            lesson_id=lesson_id,
            learning_phase=progress_phase,
            learning_type=learning_type,
            difficulty_level=difficulty_level
        )

        # Serialize the content
        content = ContentSerializer(content_queryset, many=True).data

    elif progress_phase.endswith('EXAM'):
        if progress_phase == LearningPhase.VARK_EXAM.value:
            questions_queryset = Question.objects.filter(
                learning_phase=progress_phase,
            ).exclude(
                difficulty=DifficultyLevel.CHALLENGING
            )

        elif progress_phase == LearningPhase.CONCEPTUAL_EXAM.value:
            if user_lesson_progress.study_level == DifficultyLevel.BEGINNER.value:
                questions_queryset = Question.objects.filter(
                    lesson_id=lesson_id,
                    learning_phase=progress_phase,
                    difficulty=DifficultyLevel.BEGINNER.value
                ).exclude(
                    difficulty=DifficultyLevel.CHALLENGING
                )

            elif user_lesson_progress.study_level == DifficultyLevel.INTERMEDIATE.value:
                questions_queryset = Question.objects.filter(
                    lesson_id=lesson_id,
                    learning_phase=progress_phase,
                    difficulty__in=[DifficultyLevel.BEGINNER.value, DifficultyLevel.INTERMEDIATE.value]
                ).exclude(
                    difficulty=DifficultyLevel.CHALLENGING
                )

            elif user_lesson_progress.study_level == DifficultyLevel.ADVANCED.value:
                questions_queryset = Question.objects.filter(
                    lesson_id=lesson_id,
                    learning_phase=progress_phase,
                ).exclude(
                    difficulty=DifficultyLevel.CHALLENGING
                )
        else:
            questions_queryset = Question.objects.filter(
                lesson_id=lesson_id,
                learning_phase=progress_phase,
            ).exclude(
                difficulty=DifficultyLevel.CHALLENGING
            )

        # Update the cause field based on progress_phase
        for question in questions_queryset:
            if progress_phase not in [
                LearningPhase.CONCEPTUAL_EXAM.value,
                LearningPhase.EXPLANATION_EXAM.value,
                LearningPhase.PREV_REVISION_EXAM.value,
            ]:
                # Set default values for each question type
                question.cause = ""
                if hasattr(question, 'mcq_question'):
                    question.mcq_question.correct_answer = ""
                elif hasattr(question, 'true_false_question'):
                    question.true_false_question.correct_answer = None  # Use None for bool
                elif hasattr(question, 'long_answer_question'):
                    question.long_answer_question.correct_answer = ""
                elif hasattr(question, 'sorting_question'):
                    question.sorting_question.correct_order = ""


        # Serialize the questions
        content = QuestionSerializer(questions_queryset, many=True).data

    else:
        content = None

    return list(content) if content is not None else None



