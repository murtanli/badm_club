from aiogram.fsm.state import State, StatesGroup


class RegisterStates(StatesGroup):
	waiting_for_fio = State()
	waiting_for_num_phone = State()
