from aiogram.dispatcher.filters.state import StatesGroup, State


class PayFSM(StatesGroup):
    PAY_TYPE = State()
    PAY_AMOUNT = State()


class PayCryptFSM(StatesGroup):
    PAY_TYPE = State()
    PAY_AMOUNT = State()


class CalculatorFSM(StatesGroup):
    COUNT_REFERRER = State()


class WithdrawMoneyFSM(StatesGroup):
    WITHDRAW_AMOUNT = State()
    WITHDRAW_TYPE = State()
    NUMBER_CARD = State()
    DATA_USER = State()


class ChangeCryptTypeFSN(StatesGroup):
    TYPE = State()


class AnswerAfterGiftFSM(StatesGroup):
    MESSAGE = State()


class SendGiftFSM(StatesGroup):
    WHOM = State()
    AMOUNT = State()