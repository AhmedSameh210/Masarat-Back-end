# Generated by Django 5.1.2 on 2024-11-09 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content_management', '0002_alter_subject_academic_year'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basecontent',
            name='learning_phase',
            field=models.CharField(choices=[('INTRO_CONTENT', 'تمهيد'), ('EXPLANATION_CONTENT', 'شرح الدرس'), ('PREVIOUS_CONTENT_CONTENT', 'مفهوم سابق'), ('PRACTICE_VIDEOS_CONTENT', 'تطبيقات'), ('EXERCISES_EXAM', 'تدريبات ديناميكيه')], max_length=50),
        ),
    ]
