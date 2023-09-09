import csv
import logging

from django.contrib import admin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import path

from telegramBot.forms import CsvImportForm
from telegramBot.models import Grade, Student, Permissions, TGBotAuth, ReasonsApplication


# Register your models here.

@admin.register(Grade)
class AdminGrade(admin.ModelAdmin):
    list_display = ('year_of_study', 'group')
    list_filter = ('year_of_study',)
    filter_horizontal = ('class_teachers',)


@admin.register(Student)
class AdminStudent(admin.ModelAdmin):
    list_display = ('grade', 'surname', 'name', 'fathers_name')
    search_fields = ('grade', 'surname', 'name', 'fathers_name')
    autocomplete_fields = ['parent']
    list_filter = ('grade__year_of_study', 'grade__group',)

    change_list_template = "telegramBot/students_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            for row in reader:
                year = int(row['year'].strip())
                group = row['group'].strip()
                name = row['name'].strip()
                surname = row['surname'].strip()
                fathers_name = row['fathers_name'].strip()
                if fathers_name == '':
                    fathers_name = '-'
                try:
                    grade = Grade.objects.get(year_of_study=year, group=group)
                except Grade.DoesNotExist:
                    grade = Grade()
                    grade.group = group
                    grade.year_of_study = year
                    grade.save()
                try:
                    student = Student.objects.get(name=name, surname=surname, fathers_name=fathers_name)
                    student.grade = grade
                    student.save()
                except Student.DoesNotExist:
                    student = Student()
                    student.grade = grade
                    student.name = name
                    student.fathers_name = fathers_name
                    student.surname = surname
                    student.save()
                try:
                    login = row['login'].strip()
                    password = row['password'].strip()
                    parent_name = row['parent_name']
                    parent_surname = row['parent_surname']
                    user = User.objects.get(username=login)
                except KeyError:
                    print('User doesnt have login/password')
                except User.DoesNotExist:
                    user = User.objects.create_user(username=login, password=password)
                    user.first_name = parent_name
                    user.last_name = parent_surname
                    user.save()
                    student.parent = user
                    student.save()
                    tgbotauth = TGBotAuth()
                    tgbotauth.user = user
                    tgbotauth.password = password
                    tgbotauth.type_of_user = 'P'
                    tgbotauth.save()

            # Create Hero objects from passed in data
            # ...
            self.message_user(request, "Your csv file has been imported")
            return redirect("..")
        form = CsvImportForm()
        payload = {"form": form}
        return render(
            request, "telegramBot/csv_form.html", payload
        )


@admin.register(Permissions)
class AdminStudentPermissions(admin.ModelAdmin):
    list_display = ('student', 'who_gave_permission', 'when_goes_out', 'date_time_permission_given', 'approved')
    autocomplete_fields = ['student', 'who_gave_permission', 'application_by_parent']
    list_filter = ('approved', 'type_of_applicant', 'finished_filling', 'when_goes_out')


@admin.register(TGBotAuth)
class AdminTGBotAuth(admin.ModelAdmin):
    list_display = ('user', 'password', 'chat_id', 'tg_user_id', 'time_logged_in')
    autocomplete_fields = ['user']
    change_list_template = "telegramBot/teachers_changelist.html"
    list_filter = ('type_of_user', 'authenticated')

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            for row in reader:
                username = row['login'].strip()
                password = row['password'].strip()
                name = row['name'].strip()
                surname = row['surname'].strip()
                is_admin = True if row['is_admin'] is not None and row['is_admin'] == '1' else False
                grades = []

                raw_grades = row['class_teacher'].split(',')
                for raw_grade in raw_grades:
                    try:
                        year, group = raw_grade.strip().split('-')
                    except ValueError:
                        year = None
                        group = None
                        print('passing')
                    if year is not None:
                        try:
                            grade = Grade.objects.get(year_of_study=int(year.strip()), group=group.strip())
                        except Grade.DoesNotExist:
                            grade = Grade()
                            grade.group = group
                            grade.year_of_study = year
                            grade.save()
                        grades.append(grade)

                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    user = User.objects.create_user(username=username, password=password)
                    user.last_name = surname
                    user.first_name = name
                    user.is_staff = is_admin
                    user.is_superuser = is_admin
                    user.save()

                try:
                    tg_bot_auth = TGBotAuth.objects.get(user=user)
                except TGBotAuth.DoesNotExist:
                    tg_bot_auth = TGBotAuth()
                    tg_bot_auth.password = password
                    tg_bot_auth.user = user
                    tg_bot_auth.save()

                for grade in grades:
                    grade.class_teachers.add(user)

            # Create Hero objects from passed in data
            # ...
            self.message_user(request, "Your csv file has been imported")
            return redirect("..")
        form = CsvImportForm()
        payload = {"form": form}
        return render(
            request, "telegramBot/csv_form.html", payload
        )


@admin.register(ReasonsApplication)
class AdminReasons(admin.ModelAdmin):
    list_display = ('reason',)
