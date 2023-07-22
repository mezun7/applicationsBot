from aiogram import Bot
from aiogram.utils.markdown import text, bold, italic
from asgiref.sync import sync_to_async

from telegramBot.models import TGBotAuth, Permissions
from telegramBot.utils.dao import get_tg_auth_staff


@sync_to_async
def get_messages_to_staff(bot: Bot, permission: Permissions):
    tg_bot_auths = TGBotAuth.objects.filter(user__is_staff=True, authenticated=True)
    message_text = text(bold('Ученик:'), f'{permission.student}\n', bold('Учитель:'),
                        f'{permission.who_gave_permission.last_name} {permission.who_gave_permission.first_name}\n',
                        bold('Причина:'), f'{permission.reason}', sep=' ')

    return [auth.chat_id for auth in tg_bot_auths], message_text


