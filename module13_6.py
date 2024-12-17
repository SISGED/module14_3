from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio

api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

kb1=ReplyKeyboardMarkup(resize_keyboard=True)
button3=KeyboardButton(text='Рассчитать')
button4=KeyboardButton(text='Информация')
button5=KeyboardButton(text='Купить продукт')
kb1.row(button3, button4, button5)

kb=InlineKeyboardMarkup(resize_keyboard=True)
button=InlineKeyboardButton(text='Рассчитать норму калорий', callback_data='calories')
button2=InlineKeyboardButton(text='Формулы расчёта', callback_data='formulas')
kb.row(button, button2)

prod_kb=InlineKeyboardMarkup(resize_keyboard=True)
prod_button1=InlineKeyboardButton(text='Product1', callback_data='product_buying')
prod_button2=InlineKeyboardButton(text='Product2', callback_data='product_buying')
prod_button3=InlineKeyboardButton(text='Product3', callback_data='product_buying')
prod_button4=InlineKeyboardButton(text='Product4', callback_data='product_buying')
prod_kb.add(prod_button1, prod_button2, prod_button3, prod_button4)

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

@dp.message_handler(commands=['start'])
async def start(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup=kb1)

@dp.message_handler(text='Информация')
async def inform(message):
    await message.answer('Информация о боте!')

@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup=kb)

@dp.message_handler(text='Купить продукт')
async def get_buying_list(message):
    for i in range(1, 5):
        await message.answer(f'Название: Product{i}| Описание: описание{i}| Цена: {i*100}')
        with open(f'{i}.jpg', 'rb') as img:
            await message.answer_photo(img)
    await message.answer('Выберите продукт для покупки:', reply_markup=prod_kb)

@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')
    await call.answer()

@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('Для мужчин: 10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5\n'
                              'Для женщин: 10 x вес (кг) + 6,25 x рост (см) – 5 x возраст (г) – 161')
    await call.answer()

@dp.callback_query_handler(text='calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:')
    await call.answer()
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=float(message.text))
    await message.answer('Введите свой рост (см.):')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=float(message.text))
    await message.answer('Введите свой вес (кг.):')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=float(message.text))
    data = await state.get_data()
    calories = 10 * float(data['weight']) + 6.25 * float(data['growth']) - 5 * float(data['age'])
    await message.answer(f'Ваша норма калорий, необходимая для '
                         f'функционирования организма - {calories} калорий.')
    await state.finish()


@dp.message_handler()
async def all_massages(message):
    await message.answer('Введите команду /start, чтобы начать общение.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)