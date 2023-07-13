from aiogram.filters.callback_data import CallbackData

# cb_student = CallbackData('action', 'pk')


class MainCallback(CallbackData, prefix="main"):
    action: str
    pk: int
