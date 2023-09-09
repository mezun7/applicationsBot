from aiogram import Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.markdown import text, bold, italic
from asgiref.sync import sync_to_async

from telegramBot.bot.cb_data import MainCallback
# from telegramBot.bot.keyboards import get_approval_keyboard
from telegramBot.bot.states import MyStates
from telegramBot.models import TGBotAuth, Permissions
from telegramBot.utils.dao import get_tg_auth_staff


@sync_to_async
def get_messages_to_staff(bot: Bot, permission: Permissions):
    tg_bot_auths = TGBotAuth.objects.filter(user__is_staff=True, authenticated=True)
    parent_message_header = ''
    parent_message_source = ''
    if permission.type_of_applicant == 'P':
        parent_message_header = bold('Родитель: ')
        parent_message_source = f'{permission.application_by_parent.last_name.strip()} ' + f'{permission.application_by_parent.first_name.strip()}\n'
        print(parent_message_source)
    message_text = text(bold('Ученик: '), f'{permission.student}\n', bold('Учитель: '),
                        f'{permission.who_gave_permission.last_name} {permission.who_gave_permission.first_name}\n',
                        parent_message_header, parent_message_source, bold('Причина: '), f'{permission.reason}', sep='')
    print(message_text)
    return [auth.chat_id for auth in tg_bot_auths], message_text


@sync_to_async()
def get_class_teachers_info(bot: Bot, permission: Permissions):
    message_text = f'Вам на согласование поступила заявка на выход ученика {permission.student}. ' \
                   f'Дата: {permission.when_goes_out}. Для того, чтобы ' \
                   f'согласовать/не согласовать необходимо выбрать соответствующую кнопку.'

    builder = InlineKeyboardBuilder()
    builder.button(text=f'Согласовать', callback_data=MainCallback(action='approve_student', pk=permission.pk))
    builder.button(text=f'Не согласовать', callback_data=MainCallback(action='not_approve_student', pk=permission.pk))
    builder.adjust(2)

    state_next = MyStates.main
    tg_bot_auths = TGBotAuth.objects.filter(user__grade=permission.student.grade)
    return builder.as_markup(), message_text, state_next, [auth.chat_id for auth in tg_bot_auths]


@sync_to_async
def send_back_approved_message(bot: Bot, permission: Permissions):
    pass


@sync_to_async()
def send_notification_for_admins(bot: Bot, permission: Permissions):
    pass