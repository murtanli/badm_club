from aiogram.fsm.state import State, StatesGroup


class Top_up_balance(StatesGroup):
	waiting_for_balance_amount = State()
	waiting_for_confirm = State()
