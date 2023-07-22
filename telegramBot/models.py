from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from django.db import models

from telegramBot.utils.random_str_generator import gen_string

APPROVED_CHOICES = (
    ('AP', 'APPROVED'),
    ('NAP', 'NOT_APPROVED'),
    ('NS', 'NOT_SEEN')
)

TYPE_OF_APPLICANT_CHOICES = (
    ('P', 'PARENT'),
    ('T', 'TEACHER')
)


# Create your models here.

class Grade(models.Model):
    year_of_study = models.IntegerField(verbose_name='Год обучения')
    group = models.CharField(max_length=5, verbose_name='Группа')
    class_teachers = models.ManyToManyField(User, verbose_name='Классные руководители', blank=True)

    def __str__(self):
        return f'{self.year_of_study}-{self.group}'


class Student(models.Model):
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, verbose_name='Класс')
    name = models.CharField(max_length=100, verbose_name='Имя')
    surname = models.CharField(max_length=100, verbose_name='Фамилия')
    fathers_name = models.CharField(max_length=100, verbose_name='Отчество')
    lives_in_dormitory = models.BooleanField(default=True, verbose_name='Живет в интернате?')
    can_go_home_in_the_end_of_the_week = models.BooleanField(default=False, verbose_name='Может уходить домой '
                                                                                         'самостоятельно в к'
                                                                                         'онце недели?')
    parent = models.ForeignKey(User, null=True, verbose_name=u'Родитель', on_delete=models.SET_NULL)

    def __str__(self):
        return f'{self.surname} {self.name} {self.fathers_name} ({self.grade})'


class Permissions(models.Model):
    who_gave_permission = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Кто выдал разрешение?')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='Кому разрешение выдано?')
    date_time_permission_given = models.DateTimeField(auto_now=True)
    when_goes_out = models.DateTimeField(auto_now=True)
    reason = models.CharField(max_length=2000, blank=True)
    finished_filling = models.BooleanField(default=False)
    application_by_parent = models.ForeignKey(User,
                                              on_delete=models.SET_NULL,
                                              verbose_name='Кто написал заявление?',
                                              null=True,
                                              blank=True,
                                              related_name='parents_set')
    approved = models.CharField(max_length=30, choices=APPROVED_CHOICES, default='NS')
    type_of_applicant = models.CharField(max_length=30, choices=TYPE_OF_APPLICANT_CHOICES, default='T')

    def __str__(self):
        return f'{self.student} {self.when_goes_out}'


class TGBotAuth(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    chat_id = models.CharField(max_length=100, blank=True, null=True)
    tg_user_id = models.CharField(max_length=100, blank=True, null=True)
    menu_position = models.CharField(max_length=100, blank=True, null=True)
    time_logged_in = models.DateTimeField(auto_now=True, blank=True, null=True)
    password = models.CharField(max_length=100, default=gen_string)
    authenticated = models.BooleanField(default=False)
    type_of_user = models.CharField(max_length=30, choices=TYPE_OF_APPLICANT_CHOICES, default='T')
    going_with_whom_comment = models.CharField(max_length=500, null=True, blank=True, verbose_name='С кем уходит?')

    # def __str__(self):
    #     return f'{self.user}'


class GoingWithWhomReasons(models.Model):
    reason = models.CharField(max_length=1000)

    def __str__(self):
        return self.reason


class ReasonsApplication(models.Model):
    reason = models.CharField(max_length=3000)
