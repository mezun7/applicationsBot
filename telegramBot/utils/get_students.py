from datetime import datetime

from telegramBot.models import Student, Permissions


def get_students(students):
    return [str(student) for student in students]


def get_permissions(date=datetime.now()):
    current_day = date.day
    current_month = date.month
    current_year = date.year

    students = Student.objects.filter(permissions__when_goes_out__day=current_day,
                                      permissions__when_goes_out__month=current_month,
                                      permissions__when_goes_out__year=current_year).distinct().order_by('surname',
                                                                                                         'name',
                                                                                                         'fathers_name')

    return [student for student in students]


def get_formatted_students(date=datetime.now(), max_rows=15):
    students: [Student] = get_permissions(date)
    if len(students) < max_rows:
        return get_students(students), []
    else:

        return get_students(students[:len(students) // 2]), get_students(students[len(students) // 2:])
