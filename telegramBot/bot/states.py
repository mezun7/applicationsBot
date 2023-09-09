from aiogram.fsm.state import StatesGroup, State


class MyStates(StatesGroup):
    auth_process = State()
    grade_choosing = State()
    student_choosing = State()
    reason_choosing = State()
    reason_another = State()
    not_approved_application = State()
    main = State()


class ParentsState(StatesGroup):
    main = State()
    student_choosing = State()
    date_choosing = State()
    reason_choosing = State()
    with_whom_choosing = State()
