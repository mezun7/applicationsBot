# Generated by Django 4.2.3 on 2023-07-23 19:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('telegramBot', '0012_tgbotauth_going_with_whom_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='permissions',
            name='with_whom_goes_out',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.CreateModel(
            name='ReferenceApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime_asked', models.DateTimeField(auto_now=True)),
                ('done', models.BooleanField(default=False)),
                ('type_of_reference', models.CharField(choices=[('S', 'Справка с места учебы'), ('U', 'Неизвестно')], default='U', max_length=200)),
                ('parent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('student', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='telegramBot.student')),
            ],
        ),
    ]