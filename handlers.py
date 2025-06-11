from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

router = Router()

# Главное меню клиента
client_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📅 Записаться")],
        [KeyboardButton(text="🗓 Мои записи"), KeyboardButton(text="❌ Отменить запись")],
        [KeyboardButton(text="ℹ️ О мастере")]
    ],
    resize_keyboard=True
)

# Меню администратора
admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📆 Записи на сегодня")],
        [KeyboardButton(text="👥 Добавить бесплатного клиента")],
        [KeyboardButton(text="📊 Итоги дня")],
        [KeyboardButton(text="📴 Назначить выходной день")],
        [KeyboardButton(text="📨 Сделать рассылку")],
        [KeyboardButton(text="📂 Мои данные")],
        [KeyboardButton(text="🔙 Назад")]
    ],
    resize_keyboard=True
)

@router.message(F.text == "/start")
async def start_handler(message: Message):
    await message.answer(
        "👋 Привет, красавица!\n\n"
        "Я — бот записи к мастеру Жене.\n"
        "Выбери, что тебе нужно 👇",
        reply_markup=client_menu
    )

@router.message(F.text == "/admin")
async def admin_panel(message: Message):
    await message.answer("👩‍💼 Админ-панель", reply_markup=admin_menu)

@router.message(F.text == "ℹ️ О мастере")
async def about_master(message: Message):
    await message.answer("Я Женя, мастер с 5+ летним стажем, работаю на качественных материалах. Мои работы — @jenea_nails 💖")

@router.message(F.text == "📅 Записаться")
async def book(message: Message):
    await message.answer("Запись пока вручную. Напиши дату и время в ответ.")

@router.message(F.text == "🗓 Мои записи")
async def my_bookings(message: Message):
    await message.answer("Ты записана на 15 июня в 13:00")

@router.message(F.text == "❌ Отменить запись")
async def cancel_booking(message: Message):
    await message.answer("Ты уверена, что хочешь отменить запись на 15 июня в 13:00?\n\n🔁 Да / ❌ Нет")

# Админ-функции (заглушки)
@router.message(F.text == "📆 Записи на сегодня")
async def today_records(message: Message):
    await message.answer("Сегодня записаны:\n– Анна, 12:00\n– Ирина, 14:00\nБесплатные:\n– Марина, 16:00")

@router.message(F.text == "📊 Итоги дня")
async def day_summary(message: Message):
    await message.answer("Итоги за сегодня:\n– Клиентов: 5\n– Бесплатных: 1\n– Выручка: 1200 лей")

@router.message(F.text == "📴 Назначить выходной день")
async def set_day_off(message: Message):
    await message.answer("Введите дату выходного в формате ДД.ММ.ГГГГ")

@router.message(F.text == "📨 Сделать рассылку")
async def broadcast(message: Message):
    await message.answer("Напиши текст рассылки")

@router.message(F.text == "📂 Мои данные")
async def my_data(message: Message):
    await message.answer("Ты администратор, Женя 🌸")

@router.message(F.text == "🔙 Назад")
async def go_back(message: Message):
    await message.answer("Главное меню", reply_markup=client_menu)
