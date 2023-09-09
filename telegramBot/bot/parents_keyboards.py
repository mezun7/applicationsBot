import aiogram
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from asgiref.sync import sync_to_async, async_to_sync

from telegramBot.bot.messages import MESSAGES
from telegramBot.bot.states import ParentsState
from telegramBot.models import TGBotAuth, Student


@sync_to_async
def get_parents_main_keyboard():
    print('here 2')
    builder = ReplyKeyboardBuilder()
    builder.button(text=f'Заявление на выход')
    builder.button(text=f'Запрос справки с места обучения')
    builder.adjust(1)
    markup = builder.as_markup()
    print(markup)
    return markup, MESSAGES['parents_main'], ParentsState.main


#
@sync_to_async
def get_parents_student_keyboard(tg_bot_auth):

    parent = tg_bot_auth.user

    students = Student.objects.filter(parent=parent)
    print(len(students))
    # return aiogram.types.ReplyKeyboardRemove(), 'None', None
    builder = ReplyKeyboardBuilder()
    # if len(students) == 1:
    #     return get_date_chooser_parents()
    for student in students:
        builder.button(text=f'{student.surname} {student.name} {student.fathers_name}')
    builder.adjust(1)
    return builder.as_markup(), MESSAGES['parents_students'], ParentsState.student_choosing


@sync_to_async
def get_date_chooser_parents():
    keyboard_markup = aiogram.types.ReplyKeyboardRemove()
    message_text = MESSAGES['parent_data_choosing']
    state_next = ParentsState.date_choosing
    return keyboard_markup, message_text, state_next


@sync_to_async
def get_parents_reasons_keyboard(tg_bot_auth: TGBotAuth):
    keyboard_markup = aiogram.types.ReplyKeyboardRemove()
    message_text = MESSAGES['parent_reason_choosing']
    state_next = ParentsState.reason_choosing
    return keyboard_markup, message_text, state_next


@sync_to_async
def get_parents_with_whom_goes_out(tg_bot_auth: TGBotAuth):
    keyboard_markup = aiogram.types.ReplyKeyboardRemove()
    message_text = MESSAGES['parent_with_whom_goes_out']
    state_next = ParentsState.with_whom_choosing
    return keyboard_markup, message_text, state_next


@sync_to_async
def get_reference_application_keyboard(tg_bot_auth: TGBotAuth):
    return get_parents_main_keyboard(tg_bot_auth)
