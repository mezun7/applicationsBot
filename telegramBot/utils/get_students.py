from telegramBot.models import Student


def get_students(students):
    return [str(student) for student in students]


def get_permissions(date=None):
    students = Student.objects.all()

    return [student for student in students]


def get_formatted_students(date=None, max_rows=15):
    students: [Student] = get_permissions(date)
    if len(students) < max_rows:
        return get_students(students), []
    else:

        return get_students(students[:len(students) // 2]), get_students(students[len(students) // 2:])
