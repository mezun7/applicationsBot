# Generated by Django 4.2.3 on 2023-07-22 19:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('telegramBot', '0008_student_can_go_home_in_the_end_of_the_week_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='permissions',
            name='application_by_parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parents_set', to=settings.AUTH_USER_MODEL, verbose_name='Кто написал заявление?'),
        ),
        migrations.AddField(
            model_name='permissions',
            name='approved',
            field=models.CharField(choices=[('AP', 'APPROVED'), ('NAP', 'NOT_APPROVED'), ('NS', 'NOT_SEEN')], default='NS', max_length=30),
        ),
        migrations.AddField(
            model_name='permissions',
            name='type_of_applicant',
            field=models.CharField(choices=[('P', 'PARENT'), ('T', 'TEACHER')], default='T', max_length=30),
        ),
    ]
