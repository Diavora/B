# states.py

from aiogram.fsm.state import State, StatesGroup

class TopUpState(StatesGroup):
    choosing_country = State()
    choosing_bank = State()
    entering_amount = State()
    confirming_payment = State()

class WithdrawState(StatesGroup):
    choosing_country = State()
    choosing_bank = State()
    entering_amount = State()
    entering_requisites = State()
    confirming_withdrawal = State()

class SellItemState(StatesGroup):
    name = State()
    description = State()
    price = State()
    game = State()
    confirm = State()
