from datetime import datetime

import aiogram
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, \
    ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder, KeyboardBuilder, ReplyKeyboardBuilder
from asgiref.sync import sync_to_async

from telegramBot.bot.cb_data import MainCallback
from telegramBot.bot.messages import MESSAGES
from telegramBot.bot.states import MyStates, ParentsState
from telegramBot.models import Grade, TGBotAuth, Student, ReasonsApplication, Permissions

menu = [
    [InlineKeyboardButton(text="📝 Генерировать текст", callback_data="generate_text"),
     InlineKeyboardButton(text="🖼 Генерировать изображение", callback_data="generate_image")],
    [InlineKeyboardButton(text="💳 Купить токены", callback_data="buy_tokens"),
     InlineKeyboardButton(text="💰 Баланс", callback_data="balance")],
    [InlineKeyboardButton(text="💎 Партнёрская программа", callback_data="ref"),
     InlineKeyboardButton(text="🎁 Бесплатные токены", callback_data="free_tokens")],
    [InlineKeyboardButton(text="🔎 Помощь", callback_data="help")]
]
menu = InlineKeyboardMarkup(inline_keyboard=menu)
exit_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="◀️ Выйти в меню")]], resize_keyboard=True)
iexit_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="◀️ Выйти в меню", callback_data="menu")]])


def get_students_for_keyboard(grade: Grade):
    now = datetime.now()
    students = Student.objects.filter(grade=grade). \
        exclude(permissions__when_goes_out__day=now.day,
                permissions__when_goes_out__month=now.month,
                permissions__when_goes_out__year=now.year,
                permissions__finished_filling=True).order_by('surname', 'name', 'fathers_name')
    builder = ReplyKeyboardBuilder()
    for student in students:
        builder.button(
            text=f'{student.surname.capitalize()} {student.name.capitalize()} {student.fathers_name.capitalize()}',
            callback_data=MainCallback(action='student', pk=f'{student.pk}').pack())
    builder.adjust(1)
    return builder.as_markup(), MESSAGES['student_choice'], MyStates.student_choosing


@sync_to_async
def get_keyboard_students(grade: Grade):
    return get_students_for_keyboard(grade)


@sync_to_async
def get_main_keyboard(tg_bot_auth: TGBotAuth):
    user = tg_bot_auth.user
    builder = ReplyKeyboardBuilder()
    if tg_bot_auth.type_of_user == 'P':
        builder.button(text=f'Заявление на выход')
        builder.button(text=f'Запрос справки с места обучения')
        builder.adjust(1)
        markup = builder.as_markup()
        print(markup)
        return markup, MESSAGES['parents_main'], ParentsState.main
        # return get_parents_main_keyboard()

    grades = Grade.objects.filter(class_teachers__in=[tg_bot_auth.user], student__isnull=False).distinct().order_by(
        'year_of_study', 'group')
    if user.is_staff or user.is_superuser:
        grades = Grade.objects.filter(student__isnull=False).distinct().order_by('year_of_study', 'group')

    if len(grades) == 1:
        return get_students_for_keyboard(grades[0])
    for grade in grades:
        builder.button(text=f'{grade.year_of_study}-{grade.group}',
                       callback_data=MainCallback(action='grade', pk=f'{grade.pk}').pack())

    builder.adjust(4)

    return builder.as_markup(), MESSAGES['grade_choice'], MyStates.grade_choosing


@sync_to_async
def get_reasons_keyboard():
    builder = ReplyKeyboardBuilder()
    reasons = ReasonsApplication.objects.all()
    if len(reasons) == 0:
        return aiogram.types.ReplyKeyboardRemove(), MESSAGES['reason_another'], MyStates.reason_another
    for reason in reasons:
        builder.button(text=reason.reason)
    builder.button(text=f'Другое')
    builder.adjust(1)
    return builder.as_markup(), MESSAGES['reason_choice'], MyStates.reason_choosing

# @sync_to_async
# def get_approval_keyboard(permission: Permissions):
#     print(f'permv_id: {permission.pk}')
#     text = f'Вам на согласование поступила заявка на выход ученика {permission.student}. Для того, чтобы ' \
#            f'согласовать/не согласовать необходимо выбрать соответствующую кнопку.'
#
#     builder = InlineKeyboardBuilder()
#     builder.button(text=f'Согласовать', callback_data=MainCallback(action='approve_student', pk=permission.pk))
#     builder.button(text=f'Не согласовать', callback_data=MainCallback(action='not_approve_student', pk=permission.pk))
#     builder.adjust(2)
#
#     state_next = MyStates.main
#
#     return builder.as_markup(), text, state_next
