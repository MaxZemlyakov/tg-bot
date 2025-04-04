from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio

# Жестко закодированные данные
API_TOKEN = "7523149130:AAEdNU6qIufnERaQktoM2ZeMJ4OsGemO3kY"  # Замените на ваш токен Telegram
ADMIN_ID = 715337316         # Замените на ваш Telegram ID

# Инициализация бота и роутера
bot = Bot(token=API_TOKEN)
router = Router()
dp = Dispatcher()

# Определение состояний FSM
class Form(StatesGroup):
    name = State()          # Имя гостя
    partner_name = State()  # Имя пары (если есть)
    drinks = State()        # Предпочтения по напиткам
    custom_drink = State()  # Состояние для ввода пользовательского напитка

# Команда /start
@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await message.answer(
        "Привет! 🎉 Спасибо, что откликнулись на наше предложение! Пожалуйста, поделитесь информацией о себе.",
        reply_markup=ReplyKeyboardRemove()
    )
    await message.answer("Введите ваше имя:")
    await state.set_state(Form.name)

# Обработка имени
@router.message(Form.name)
async def process_name(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await state.clear()
        await message.answer("Действие отменено.", reply_markup=ReplyKeyboardRemove())
        return
    await state.update_data(name=message.text)
    await message.answer("Если вы хотите пригласить пару, введите её имя. Если нет, напишите 'нет'.")
    await state.set_state(Form.partner_name)

# Обработка имени пары
@router.message(Form.partner_name)
async def process_partner_name(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await state.clear()
        await message.answer("Действие отменено.", reply_markup=ReplyKeyboardRemove())
        return
    await state.update_data(partner_name=message.text)
    # Кнопки выбора напитков
    drinks_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Безалкогольные")],
            [KeyboardButton(text="Красное вино"), KeyboardButton(text="Белое вино")],
            [KeyboardButton(text="Сухое вино"), KeyboardButton(text="Полусладкое вино")],
            [KeyboardButton(text="Игристое вино"), KeyboardButton(text="Водка")],
            [KeyboardButton(text="Самогон"), KeyboardButton(text="Коньяк")],
            [KeyboardButton(text="Настойки")],
            [KeyboardButton(text="Другое")],  # Новая кнопка для пользовательского напитка
            [KeyboardButton(text="Готово"), KeyboardButton(text="Отмена")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    await message.answer(
        "Выберите предпочитаемые напитки (нажмите 'Готово', когда закончите):",
        reply_markup=drinks_keyboard
    )
    await state.update_data(drinks=[])  # Инициализация списка для хранения выбранных напитков
    await state.set_state(Form.drinks)

# Обработка выбора напитков
@router.message(Form.drinks)
async def process_drinks(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await state.clear()
        await message.answer("Действие отменено.", reply_markup=ReplyKeyboardRemove())
        return
    if message.text.lower() == "готово":
        data = await state.get_data()
        guest_info = (
            f"🎉 Новый гость:\n"
            f"Имя: {data['name']}\n"
            f"Пара: {data['partner_name']}\n"
            f"Предпочитаемые напитки: {', '.join(data['drinks']) if data['drinks'] else 'Не указаны'}"
        )
        # Отправка информации администратору
        await bot.send_message(chat_id=ADMIN_ID, text=guest_info)
        # Сообщение пользователю
        await message.answer("Спасибо за предоставленную информацию! 🎉", reply_markup=ReplyKeyboardRemove())
        await state.clear()  # Завершение состояния
        return
    if message.text.lower() == "другое":
        await message.answer("Введите название вашего предпочтительного напитка:")
        await state.set_state(Form.custom_drink)
        return
    # Добавление выбранного напитка в список
    data = await state.get_data()
    drinks = data.get('drinks', [])
    if message.text not in drinks:
        drinks.append(message.text)
        await state.update_data(drinks=drinks)
    await message.answer(f"Вы выбрали: {message.text}. Выберите еще или нажмите 'Готово'.")

# Обработка пользовательского напитка
@router.message(Form.custom_drink)
async def process_custom_drink(message: Message, state: FSMContext):
    if message.text.lower() == "отмена":
        await state.clear()
        await message.answer("Действие отменено.", reply_markup=ReplyKeyboardRemove())
        return
    # Добавление пользовательского напитка в список
    data = await state.get_data()
    drinks = data.get('drinks', [])
    drinks.append(message.text)
    await state.update_data(drinks=drinks)
    await message.answer(f"Вы добавили: {message.text}. Выберите еще или нажмите 'Готово'.")
    await state.set_state(Form.drinks)

# Запуск бота
async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
