from django.shortcuts import render

from telegramBot.models import Student
from telegramBot.utils.get_students import get_formatted_students


# Create your views here.

def home(request):
    students_col1, students_col2 = get_formatted_students()
    context = {
        'students_col1': students_col1,
        'students_col2': students_col2
    }

    return render(request, template_name='telegramBot/list_of_permissions.html', context=context)
