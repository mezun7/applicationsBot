from datetime import datetime

from telegramBot.models import Student, Permissions


def get_students(students):
    return [str(student) for student in students]


def get_permissions(date=None):
    current_day = datetime.now().day
    current_month = datetime.now().month
    current_year = datetime.now().year
    permissions = Permissions.objects.filter(when_goes_out__day=current_day,
                                             when_goes_out__month=current_month,
                                             when_goes_out__year=current_year)
    students = permissions.students_set.all()

    return [student for student in students]


def get_formatted_students(date=None, max_rows=15):
    students: [Student] = get_permissions(date)
    if len(students) < max_rows:
        return get_students(students), []
    else:

        return get_students(students[:len(students) // 2]), get_students(students[len(students) // 2:])
