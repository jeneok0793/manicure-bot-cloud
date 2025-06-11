from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMIN_CHAT_ID

router = Router()

# Главная клавиатура для клиента
def client_main_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📅 Записаться")],
            [KeyboardButton(text="🗓 Мои записи"), KeyboardButton(text="❌ Отменить запись")],
            [KeyboardButton(text="ℹ️ О мастере")]
        ],
        resize_keyboard=True
    )

# Клавиатура админа
def admin_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📆 Записи на сегодня")],
            [KeyboardButton(text="👥 Добавить бесплатного клиента")],
            [KeyboardButton(text="📊 Итоги дня"), KeyboardButton(text="📴 Назначить выходной день")],
            [KeyboardButton(text="📨 Сделать рассылку"), KeyboardButton(text="📂 Мои данные")]
        ],
        resize_keyboard=True
    )

@router.message(F.text == "/start")
async def cmd_start(message: Message):
    if message.chat.id == ADMIN_CHAT_ID:
        await message.answer("👩‍💼 Админ-панель", reply_markup=admin_keyboard())
    else:
        await message.answer(
            "👋 Привет, красавица!\n\n"
            "Я — бот записи к мастеру Жене. Выбери, что тебе нужно 👇",
            reply_markup=client_main_keyboard()
        )

@router.message(F.text == "📅 Записаться")
async def record(message: Message):
    await message.answer("Выбери удобную дату из доступных 👇 (функционал записи будет добавлен)")

@router.message(F.text == "🗓 Мои записи")
async def my_record(message: Message):
    await message.answer("Ты записана на 15 июня в 13:00 (пример)")

@router.message(F.text == "❌ Отменить запись")
async def cancel_record(message: Message):
    await message.answer("Ты уверена, что хочешь отменить запись на 15 июня в 13:00?\n\n🔁 Да / ❌ Нет")

@router.message(F.text == "ℹ️ О мастере")
async def about(message: Message):
    await message.answer(
        "💅 Я Женя, мастер с 5+ летним стажем.\n"
        "Работаю только на качественных материалах.\n"
        "Мои работы — в Instagram: @jenea_nails 💖"
    )

# Команды админа

@router.message(F.text == "📆 Записи на сегодня")
async def today_records(message: Message):
    await message.answer(
        "Сегодня записаны:\n"
        "– Анна, 12:00\n"
        "– Ирина, 14:00\n"
        "Бесплатные:\n"
        "– Марина, 16:00"
    )

@router.message(F.text == "📊 Итоги дня")
async def daily_summary(message: Message):
    await message.answer(
        "Итоги за сегодня:\n"
        "– Клиентов: 5\n"
        "– Бесплатных: 1\n"
        "– Выручка: 1200 лей"
    )

@router.message(F.text == "📴 Назначить выходной день")
async def set_day_off(message: Message):
    await message.answer("Введите дату выходного в формате ДД.ММ.ГГГГ")

@router.message(F.text == "📨 Сделать рассылку")
async def mailing(message: Message):
    await message.answer("Напиши текст рассылки. После этого добавим кнопку 'Записаться'")

@router.message(F.text == "📂 Мои данные")
async def my_data(message: Message):
    await message.answer("Ваш ID: " + str(message.chat.id))
