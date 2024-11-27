# Generated by Django 5.1.2 on 2024-11-05 05:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content_management', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subject',
            name='academic_year',
            field=models.CharField(choices=[('Primary 1', 'الصف الأبتدائي الأول'), ('Primary 2', 'الصف الابتدائي الثاني'), ('Primary 3', 'الصف الابتداائي الثالث'), ('Primary 4', 'الصف الابتدائي الرابع'), ('Primary 5', 'الصف الابتدائي الخامس'), ('Primary 6', 'الصف الابتدائي السادس'), ('Prep 1', 'الصف الأعدادي الأول'), ('Prep 2', 'الصق الأعدادي الثاني'), ('Prep 3', 'الصف الأعدادي الثالث'), ('Secondary 1', 'الصف الثانوي الأول'), ('Secondary 2', 'الصف الثانوي الثاني'), ('Secondary 3', 'الصف الثانوي الثالث'), ('VARK', 'VARK')], max_length=20),
        ),
    ]