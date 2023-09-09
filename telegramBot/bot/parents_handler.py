import datetime
import logging

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from telegramBot.bot import main
from telegramBot.bot.keyboards import get_reasons_keyboard
from telegramBot.bot.messages import MESSAGES
from telegramBot.bot.parents_keyboards import get_reference_application_keyboard, get_parents_student_keyboard, \
    get_parents_main_keyboard, get_parents_reasons_keyboard, get_parents_with_whom_goes_out, get_date_chooser_parents
from telegramBot.bot.states import ParentsState
from telegramBot.models import TGBotAuth, Student, Permissions
from telegramBot.utils.dao import get_user_for_tg_bot_auth, get_user_for_student
from telegramBot.utils.sender import get_class_teachers_info

parents_router = Router()


@parents_router.message(ParentsState.main)
async def parents_main(msg: Message, state: FSMContext):
    tg_bot_auth = await TGBotAuth.objects.aget(tg_user_id=msg.from_user.id)
    print(tg_bot_auth.tg_user_id, 'Here')
    keyboard_markup, text, state_next = None, None, None
    if msg.text == 'Запрос справки с места обучения':
        keyboard_markup, text, state_next = await get_reference_application_keyboard(tg_bot_auth)
    elif msg.text == 'Заявление на выход':
        print(msg.from_user.id)

        keyboard_markup, text, state_next = await get_parents_student_keyboard(tg_bot_auth)
    await state.set_state(state_next)
    await msg.answer(text=text, reply_markup=keyboard_markup)


@parents_router.message(ParentsState.student_choosing)
async def parents_student_handler(msg: Message, state: FSMContext):
    tg_bot_auth = await TGBotAuth.objects.aget(tg_user_id=msg.from_user.id)
    keyboard_markup_main, text_main, state_next_main = await get_parents_main_keyboard()
    surname, name, fathers_name = msg.text.split()
    parent = await get_user_for_tg_bot_auth(tg_bot_auth)
    student = await Student.objects.aget(name__iexact=name,
                                         surname__iexact=surname,
                                         fathers_name__iexact=fathers_name)
    student_parent = await get_user_for_student(student)
    if student_parent != parent:
        await state.set_state(state_next_main)
        await msg.answer(text_main, reply_markup=keyboard_markup_main)
        return
    keyboard_markup, text, state_next = await get_date_chooser_parents()

    permission = Permissions()
    permission.student = student
    permission.application_by_parent = parent
    permission.type_of_applicant = 'P'
    await permission.asave()
    await state.set_data({'permission_id': f'{permission.pk}'})
    await state.set_state(state_next)
    await msg.answer(text, reply_markup=keyboard_markup)


@parents_router.message(ParentsState.date_choosing)
async def parents_date_chooser(msg: Message, state: FSMContext):
    tg_bot_auth = await TGBotAuth.objects.aget(tg_user_id=msg.from_user.id)
    state_data = await state.get_data()
    message_text = msg.text.strip()
    perm_id = state_data['permission_id']

    dt = None
    now = datetime.datetime.now()
    now_dt = datetime.datetime(day=now.day, month=now.month, year=now.year)
    try:
        day, month, year = message_text.split('.')
        dt = datetime.datetime(day=int(day), month=int(month), year=int(year))
    except ValueError:
        await msg.answer(MESSAGES['date_error'])
        return
    if now_dt > dt:
        await msg.answer(MESSAGES['date_error_past'])
        return
    permission = await Permissions.objects.aget(pk=perm_id)
    permission.when_goes_out = dt
    await permission.asave()
    keyboard_markup, text, state_next = await get_parents_reasons_keyboard(tg_bot_auth)
    await state.set_data({'permission_id': f'{permission.pk}'})
    await state.set_state(state_next)
    await msg.answer(text, reply_markup=keyboard_markup)


@parents_router.message(ParentsState.reason_choosing)
async def parents_reason_chooser(msg: Message, state: FSMContext):
    tg_bot_auth = await TGBotAuth.objects.aget(tg_user_id=msg.from_user.id)
    state_data = await state.get_data()
    message_text = msg.text.strip()
    perm_id = state_data['permission_id']
    permission = await Permissions.objects.aget(pk=perm_id)
    permission.reason = message_text
    await permission.asave()
    keyboard_markup, text, state_next = await get_parents_with_whom_goes_out(tg_bot_auth)
    await state.set_data({'permission_id': f'{permission.pk}'})
    await state.set_state(state_next)
    await msg.answer(text, reply_markup=keyboard_markup)


@parents_router.message(ParentsState.with_whom_choosing)
async def parents_with_whom_chooser(msg: Message, state: FSMContext):
    state_data = await state.get_data()
    message_text = msg.text.strip()
    perm_id = state_data['permission_id']
    permission = await Permissions.objects.aget(pk=perm_id)
    permission.with_whom_goes_out = message_text
    permission.finished_filling = False
    await permission.asave()
    ct_keyboard, ct_message, ct_state, chat_ids_to_send = await get_class_teachers_info(main.bot, permission)
    print()
    for teacher_chat_id in chat_ids_to_send:
        try:
            await main.bot.send_message(chat_id=teacher_chat_id, text=ct_message, reply_markup=ct_keyboard)
            print(f'Sending to {teacher_chat_id}')
        except:
            print('Erroroorororo')
    keyboard_markup, text, state_next = await get_parents_main_keyboard()
    await state.clear()
    await state.set_state(state_next)
    await msg.answer(text=MESSAGES['parents_finished_application'])
    await msg.answer(text, reply_markup=keyboard_markup)
