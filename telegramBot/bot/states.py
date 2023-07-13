from aiogram.fsm.state import StatesGroup, State


class MyStates(StatesGroup):
    auth_process = State()
    grade_choosing = State()
    student_choosing = State()
    reason_choosing = State()
    reason_another = State()
    main = State()
