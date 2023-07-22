import asyncio
import logging

import aiogram
from aiogram import types, F, Router, Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from asgiref.sync import sync_to_async
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from applicationsBot import settings
from applicationsBot.settings import TGBOT_MEMORY
from telegramBot.bot.cb_data import MainCallback
from telegramBot.bot.keyboards import menu, get_main_keyboard, get_keyboard_students, get_reasons_keyboard
from telegramBot.bot.states import MyStates
from telegramBot.models import TGBotAuth, Student, Permissions, Grade
from telegramBot.utils.dao import get_last_permission, get_user_for_tg_bot_auth, set_permission
from telegramBot.utils.sender import get_messages_to_staff

router = Router()
dp = None
bot = None


async def main():
    global dp, bot
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=settings.BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=TGBOT_MEMORY)
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    # await dp.storage.close()


@router.message(Command("start"))
async def start_handler(msg: Message, state: FSMContext):
    await state.set_state(MyStates.auth_process)
    await msg.answer("Привет! Авторизуйтесь, используя следующую команду /login username password")


@router.message(Command("reload"))
async def start_handler(msg: Message, state: FSMContext):
    bot_auth = await TGBotAuth.objects.aget(tg_user_id=msg.from_user.id)
    keyboard_markup, text, state_next = await get_main_keyboard(bot_auth)
    await state.set_state(state_next)
    await msg.answer(text, reply_markup=keyboard_markup)


@router.message(Command("login"))
async def login_handler(msg: Message, state: FSMContext):
    user_id = msg.from_user.id
    chat_id = msg.chat.id
    # print(type(user_id))
    args = msg.text.split()
    if len(args) > 2:
        username = args[-2]
        password = args[-1]
        try:
            bot_auth = await TGBotAuth.objects.aget(user__username=username, password=password)
            bot_auth.chat_id = str(chat_id)
            bot_auth.tg_user_id = str(user_id)
            bot_auth.menu_position = '2'
            bot_auth.authenticated = True
            await bot_auth.asave()
            await msg.delete()
            keyboard_markup, text, state_next = await get_main_keyboard(bot_auth)
            await state.clear()
            await state.set_state(state_next)
            await msg.answer(text, reply_markup=keyboard_markup)

        except TGBotAuth.DoesNotExist:
            bot_auth = None
        except User.DoesNotExist:
            bot_auth = None

        if bot_auth is None:
            await msg.answer(f"Неверные логин или пароль.")
    else:
        await msg.answer(f"Недостаточно аргументов для авторизации")


@router.message(F.text.lower() == "отмена")
async def cancel_handler(msg: Message, state: FSMContext):
    await state.clear()
    bot_auth = await TGBotAuth.objects.aget(tg_user_id=msg.from_user.id)
    keyboard_markup, text, state_next = await get_main_keyboard(bot_auth)
    await state.set_state(state_next)
    await msg.answer(text=text, reply_markup=keyboard_markup)


@router.message(MyStates.grade_choosing)
async def grade_handler(msg: Message, state: FSMContext):
    year_of_study, group = msg.text.split('-')
    grade = await Grade.objects.aget(year_of_study=int(year_of_study), group=group)
    keyboard, text, state_next = await get_keyboard_students(grade)
    await state.set_state(state_next)
    await state.set_data({f'grade_pk': grade.pk})
    # await .delete_reply_markup()
    await msg.answer(text=text, reply_markup=keyboard)


# @dp.callback_query_handler(cb_student.filter(action='student'))
@router.message(MyStates.student_choosing)
async def student_handler(msg: Message, state: FSMContext):
    data = await state.get_data()
    grade = await Grade.objects.aget(pk=data['grade_pk'])
    surname, name, fathers_name = msg.text.split()
    student = await Student.objects.aget(grade=grade,
                                         name__iexact=name,
                                         surname__iexact=surname,
                                         fathers_name__iexact=fathers_name)
    user = await TGBotAuth.objects.aget(tg_user_id=msg.from_user.id)
    permission = Permissions()
    permission.student = student
    permission.who_gave_permission = await get_user_for_tg_bot_auth(user)
    await permission.asave()

    await state.set_data({'permission_id': f'{permission.pk}'})
    keyboard_markup, text, state_next = await get_reasons_keyboard()
    await state.set_state(state_next)
    await msg.answer(f'Введите, пожалуйста, причину отсутствия', reply_markup=keyboard_markup)


@router.message(MyStates.reason_choosing)
async def reason_handler(msg: Message, state: FSMContext):
    global bot
    if msg.text == 'Другое':
        await state.set_state(MyStates.reason_another)
        await msg.answer(text='Введите причину отсутствия', reply_markup=aiogram.types.ReplyKeyboardRemove())
        return
    bot_auth = await TGBotAuth.objects.aget(tg_user_id=msg.from_user.id)
    state_data = await state.get_data()
    permission = await Permissions.objects.aget(pk=state_data['permission_id'])
    await set_permission(permission, msg.text)

    # permission = await get_last_permission(bot_auth, msg.text)
    keyboard_markup, text, state_next = await get_main_keyboard(bot_auth)
    data = await state.get_data()
    tg_bot_auths, staff_message = await get_messages_to_staff(bot, permission)
    for tg_user in tg_bot_auths:
        try:
            await bot.send_message(chat_id=tg_user, text=staff_message, parse_mode=ParseMode.MARKDOWN)
        except:
            print('error')
    # print(data)
    await state.set_state(state_next)
    await state.set_data(data)
    await msg.answer(text=text, reply_markup=keyboard_markup)


@router.message(MyStates.reason_another)
async def another_reason_handler(msg: Message, state: FSMContext):
    global bot
    state_data = await state.get_data()
    permission = await Permissions.objects.aget(pk=state_data['permission_id'])
    await set_permission(permission, msg.text)
    bot_auth = await TGBotAuth.objects.aget(tg_user_id=msg.from_user.id)
    keyboard_markup, text, state_next = await get_main_keyboard(bot_auth)
    tg_bot_auths, staff_message = await get_messages_to_staff(bot, permission)
    for tg_user in tg_bot_auths:
        await bot.send_message(chat_id=tg_user, text=staff_message, parse_mode=ParseMode.MARKDOWN)
    await state.set_state(state_next)

    await msg.answer(text=text, reply_markup=keyboard_markup)
