# Generated by Django 4.2.3 on 2023-07-22 22:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telegramBot', '0011_tgbotauth_type_of_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='tgbotauth',
            name='going_with_whom_comment',
            field=models.CharField(blank=True, max_length=500, null=True, verbose_name='С кем уходит?'),
        ),
    ]
