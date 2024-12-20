# Generated by Django 5.1.2 on 2024-11-04 19:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chats', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chatmessage',
            name='content',
            field=models.JSONField(),
        ),
        migrations.AlterField(
            model_name='chatmessage',
            name='sender_type',
            field=models.CharField(choices=[('student', 'Student'), ('system', 'System')], max_length=20),
        ),
    ]
