from aiogram import Bot, Dispatcher
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from config import BOT_TOKEN, RECEIVER_ADDRESS
from crypto import get_transaction

bot = Bot(BOT_TOKEN)
dp = Dispatcher(bot)

users = {}

class TronWallet(StatesGroup):
    wallet = State()

class AddBalance(StatesGroup):
    amount = State()
    
@dp.message(CommandStart())
async def start_command(msg: Message, state: FSMContext):
    await msg.delete()
    if not msg.from_user.id in users:
        users[msg.from_user.id] = []
    await msg.answer("Добро пожаловать в бота! Пожалуйста, введите ваш адрес Tron кошелька:")
    await state.set_state(TronWallet.wallet)

@dp.message(TronWallet.wallet)
async def set_wallet(msg: Message, state: FSMContext):
    await state.clear()
    if msg.from_user.id in users:
        users[msg.from_user.id] = [msg.text, 0]
        await msg.reply("Отлично! Теперь давай пополним твой баланс: /add_balance")

@dp.message(Command("add_balance"))
async def add_balance(msg: Message, state: FSMContext):
    await state.set_state(AddBalance.amount)
    await msg.answer("Введите сумму TRX:")

@dp.message(AddBalance.amount)
async def set_amount(msg: Message, state: FSMContext):
    await state.clear()
    if msg.text.isnumeric():
        amount = int(msg.text)
        _from = users[msg.from_user.id][0]
        _to = RECEIVER_ADDRESS
        await msg.reply(f"Переведите {amount} TRX. \nСо счёта `{_from}` на `{_to}`", parse_mode="MarkdownV2",
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Я оплатил", callback_data="payment")]]))

@dp.callback_query()
async def callbacks(callback: CallbackQuery):
    if callback.data == "payment":
        amount = get_transaction(users[callback.message.from_user.id][0])
        users[callback.message.from_user.id][1] += amount if amount else await callback.answer("Вы уверены? Повторите попытку. \nТранзакция не найдена")

@dp.message(Command("balance"))
async def get_balance(msg: Message):
    await msg.answer(f"Ваш баланс - {users[msg.from_user.id][1]} TRX")

if __name__ == "__main__":
    dp.start_polling(bot)