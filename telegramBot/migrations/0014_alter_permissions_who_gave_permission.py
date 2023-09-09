# Generated by Django 4.2.3 on 2023-07-23 21:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('telegramBot', '0013_permissions_with_whom_goes_out_referenceapplication'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permissions',
            name='who_gave_permission',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Кто выдал разрешение?'),
        ),
    ]
