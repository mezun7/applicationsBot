from asgiref.sync import sync_to_async
from django.contrib.auth.models import User

from telegramBot.models import Grade, TGBotAuth, Permissions, Student


@sync_to_async
def get_last_permission(tg_bot_auth: TGBotAuth, message):
    permission = Permissions.objects.filter(who_gave_permission=tg_bot_auth.user).order_by(
        '-date_time_permission_given').first()
    permission.reason = message
    permission.save()
    return permission


@sync_to_async()
def get_user_for_tg_bot_auth(tg_bot_auth: TGBotAuth) -> User:
    return tg_bot_auth.user


@sync_to_async()
def get_user_for_student(student: Student) -> User:
    return student.parent


@sync_to_async()
def set_permission(permission: Permissions, reason: str):
    permission.reason = reason
    permission.finished_filling = True
    permission.save()


@sync_to_async()
def get_tg_auth_staff():
    tg_auths = TGBotAuth.objects.filter(user__is_staff=True)
    return tg_auths


@sync_to_async()
def get_parent_for_permission(permission: Permissions):
    return permission.application_by_parent


