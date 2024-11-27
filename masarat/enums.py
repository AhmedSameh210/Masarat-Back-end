from django.db import models

class AcademicYear(models.TextChoices):
    PRIMARY_1 = 'Primary 1', 'الصف الأبتدائي الأول'
    PRIMARY_2 = 'Primary 2', 'الصف الابتدائي الثاني'
    PRIMARY_3 = 'Primary 3', 'الصف الابتداائي الثالث'
    PRIMARY_4 = 'Primary 4', 'الصف الابتدائي الرابع'
    PRIMARY_5 = 'Primary 5', 'الصف الابتدائي الخامس'
    PRIMARY_6 = 'Primary 6', 'الصف الابتدائي السادس'

    PREP_1 = 'Prep 1', 'الصف الأعدادي الأول'
    PREP_2 = 'Prep 2', 'الصق الأعدادي الثاني'
    PREP_3 = 'Prep 3', 'الصف الأعدادي الثالث'

    SECONDARY_1 = 'Secondary 1', 'الصف الثانوي الأول'
    SECONDARY_2 = 'Secondary 2', 'الصف الثانوي الثاني'
    SECONDARY_3 = 'Secondary 3', 'الصف الثانوي الثالث'

    VARK = "VARK", "VARK"

class Major(models.TextChoices):
    SCIENCE = 'Science', 'علمي'
    ARTS = 'Arts', 'ادبي'
    COMMERCE = 'Commerce', 'تجاري'
    ENGINEERING = 'Engineering', 'هندسي'






class QuestionType(models.TextChoices):
    MULTIPLE_CHOICE = 'MULTIPLE_CHOICE', 'اختيار من متعدد'
    TRUE_FALSE = 'TRUE_FALSE', 'صواب/خطأ'
    LONG_ANSWER = 'LONG_ANSWER', 'مقالي'
    SORTING = 'SORTING', 'ترتيب'


class BloomsLevel(models.TextChoices):
    REMEMBER = 'REMEMBER', 'تذكر'
    UNDERSTAND = 'UNDERSTAND', 'فهم'
    APPLY = 'APPLY', 'تطبيق'
    ANALYZE = 'ANALYZE', 'تحليل'
    EVALUATE = 'EVALUATE', 'تقييم'
    CREATE = 'CREATE', 'ابتكار'




# Enum for emotions
class EmotionChoices(models.TextChoices):
    ANGRY = 'angry', 'غاضب'
    DISGUST = 'disgust', 'اشمئزاز'
    FEAR = 'fear', 'يخاف'
    HAPPY = 'happy', 'سعيد'
    NEUTRAL = 'neutral', 'طبيعي'
    SAD = 'sad', 'حزين' 
    SURPRISED = 'surprised', 'متفاجئ'
    Not_Attentive = 'Not-Attentive (student unavailable)', "غير موجود"




class LearningType(models.TextChoices):
    VISUAL = 'Visual', 'بصري'                 
    AUDITORY = 'Auditory', 'سمعي'           
    KINESTHETIC = 'Kinesthetic', 'تجريبي'  
    READING_WRITING = 'Reading/Writing', 'منطقي' 



class DifficultyLevel(models.TextChoices):
    BEGINNER = 'BEGINNER', 'مبتدئ'
    INTERMEDIATE = 'INTERMEDIATE', 'متوسط'
    ADVANCED = 'ADVANCED', 'متقدم'
    CHALLENGING = 'CHALLENGING', 'تنافسي'

# Enums for the questions
class LearningPhase(models.TextChoices):
    VARK_EXAM = 'VARK_EXAM', 'تقويم لتحديد نوع التعلم المفضل'
    INTRO_EXAM = 'INTRO_EXAM', 'تقويم مبدأي'
    CONCEPTUAL_EXAM = 'CONCEPTUAL_EXAM', 'تقويم بنائي علي التمهيد'
    EXPLANATION_EXAM = 'EXPLANATION_EXAM', 'تقويم بنائي علي الشرح'
    PREV_REVISION_EXAM = 'PREV_REVISION_EXAM', 'تقويم بنائي علي المفهوم السابق'
    FINAL_ASSESSMENT_EXAM = 'FINAL_ASSESSMENT_EXAM', 'التقويم الختامي'
    


class ContentLearningPhase(models.TextChoices):
    INTRO_CONTENT = 'INTRO_CONTENT', 'تمهيد' 
    EXPLANATION_CONTENT = 'EXPLANATION_CONTENT', 'شرح الدرس'
    PREVIOUS_CONTENT_CONTENT = 'PREVIOUS_CONTENT_CONTENT', 'مفهوم سابق'
    PRACTICE_VIDEOS_CONTENT = 'PRACTICE_VIDEOS_CONTENT', 'تطبيقات'
    EXERCISES_CONTENT = 'EXERCISES_CONTENT', 'تدريبات ديناميكيه'






class ContentType(models.TextChoices):
    VIDEO = 'VIDEO', 'فيديو'
    DYNAMIC = 'DYNAMIC', 'ديناميكي'







class ChatProgress(models.TextChoices):
    GREETING = 'GREETING', 'بدء المحادثه'
 
    INTRO_EXAM = 'INTRO_EXAM', 'تقويم مبدأي'
    INTRO_CONTENT = 'INTRO_CONTENT', 'تمهيد' 
    CONCEPTUAL_EXAM = 'CONCEPTUAL_EXAM', 'تقويم بنائي علي التمهيد'
  
    EXPLANATION_CONTENT = 'EXPLANATION_CONTENT', 'شرح الدرس'
    EXPLANATION_EXAM = 'EXPLANATION_EXAM', 'تقويم بنائي علي الشرح'
  
    PREVIOUS_CONTENT_CONTENT = 'PREVIOUS_CONTENT_CONTENT', 'مفهوم سابق'
    PREV_REVISION_EXAM = 'PREV_REVISION_EXAM', 'تقويم بنائي علي المفهوم السابق'


    PRACTICE_VIDEOS_CONTENT = 'PRACTICE_VIDEOS_CONTENT', 'تطبيقات'
   
    EXERCISES_CONTENT = 'EXERCISES_CONTENT', 'تدريبات ديناميكيه'
   
    FINAL_ASSESSMENT_EXAM = 'FINAL_ASSESSMENT_EXAM', 'التقويم الختامي'
