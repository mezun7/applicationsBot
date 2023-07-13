import aiogram
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, \
    ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder, KeyboardBuilder, ReplyKeyboardBuilder
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User

from telegramBot.bot.cb_data import MainCallback
from telegramBot.bot.states import MyStates
from telegramBot.models import Grade, TGBotAuth, Student, ReasonsApplication
from telegramBot.utils.dao import get_user_for_tg_bot_auth

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

MESSAGES = {
    'student_choice': 'Выберите, пожалуйста, ученика',
    'grade_choice': 'Выберите, пожалуйста, класс',
    'reason_choice': 'Выберите причину отсутствия или выберите кнопку "Другое"  и впшите причину.',
    'reason_another': 'Укажите причину отсутствия'
}


@sync_to_async
def get_keyboard_students(grade: Grade):
    students = Student.objects.filter(grade=grade).order_by('surname')
    builder = ReplyKeyboardBuilder()
    for student in students:
        builder.button(
            text=f'{student.surname.capitalize()} {student.name.capitalize()} {student.fathers_name.capitalize()}',
            callback_data=MainCallback(action='student', pk=f'{student.pk}').pack())
    builder.adjust(1)
    return builder.as_markup(), MESSAGES['student_choice'], MyStates.student_choosing


@sync_to_async
def get_main_keyboard(tg_bot_auth: TGBotAuth):
    user = tg_bot_auth.user
    grades = Grade.objects.filter(class_teachers__in=[tg_bot_auth.user]).order_by('year_of_study', 'group')
    if user.is_staff or user.is_superuser:
        grades = Grade.objects.all().order_by('year_of_study', 'group')
    builder = ReplyKeyboardBuilder()

    if len(grades) == 1:
        return get_keyboard_students(grades[0])
    for grade in grades:
        builder.button(text=f'{grade.year_of_study}-{grade.group}',
                       callback_data=MainCallback(action='grade', pk=f'{grade.pk}').pack())

    builder.adjust(2)

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
