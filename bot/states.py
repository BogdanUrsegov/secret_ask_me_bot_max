from maxapi.context import State, StatesGroup

class Sending(StatesGroup):
    wait = State()

class Responding(StatesGroup):
    wait = State()