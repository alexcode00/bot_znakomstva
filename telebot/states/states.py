from aiogram.fsm.state import StatesGroup, State


class Reg(StatesGroup):
    name = State()
    age = State()
    city = State()
    about = State()
    photo = State()
    mode = State()
    target_id = State()