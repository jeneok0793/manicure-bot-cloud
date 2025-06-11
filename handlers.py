from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

router = Router()

# Главное меню для клиента
client_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📅 Записаться")],
        [KeyboardButton(text="🗓 Мои записи"), KeyboardButton(text="❌ Отменить запись")],
        [KeyboardButton(text="ℹ️ О мастере")]
    ],
    resize_keyboard=True
)

# Меню админа
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

# Обработка кнопок клиента
@router.message(F.text == "📅 Записаться")
async def handle_book(message: Message):
    await message.answer("Выбери удобную дату для записи (в следующей версии бот покажет календарь).")

@router.message(F.text == "🗓 Мои записи")
async def handle_my_appointments(message: Message):
    await message.answer("Ты записана на 15 июня в 13:00")  # Заменим позже динамически

@router.message(F.text == "❌ Отменить запись")
async def handle_cancel(message: Message):
    await message.answer("Ты уверена, что хочешь отменить запись на 15 июня в 13:00?\n\n🔁 Да / ❌ Нет")

@router.message(F.text == "ℹ️ О мастере")
async def handle_about(message: Message):
    await message.answer("Я Женя, мастер с 5+ летним стажем. Мои работы — в Instagram @jenea_nails 💖")

# Обработка кнопок админа
@router.message(F.text == "📆 Записи на сегодня")
async def handle_today_records(message: Message):
    await message.answer("Сегодня записаны:\n– Анна, 12:00\n– Ирина, 14:00\nБесплатные:\n– Марина, 16:00")

@router.message(F.text == "👥 Добавить бесплатного клиента")
async def handle_add_free(message: Message):
    await message.answer("Введите имя и время клиента, например: Марина, 16:00")

@router.message(F.text == "📊 Итоги дня")
async def handle_day_summary(message: Message):
    await message.answer("Итоги за сегодня:\n– Клиентов: 5\n– Бесплатных: 1\n– Выручка: 1200 лей")

@router.message(F.text == "📴 Назначить выходной день")
async def handle_day_off(message: Message):
    await message.answer("Введите дату выходного в формате ДД.ММ.ГГГГ")

@router.message(F.text == "📨 Сделать рассылку")
async def handle_broadcast(message: Message):
    await message.answer("Введите текст рассылки, и я отправлю его всем клиентам")

@router.message(F.text == "📂 Мои данные")
async def handle_admin_info(message: Message):
    await message.answer("Вы: Админ\nИмя: Женя\nРасписание: Пн-Сб 10:00–18:00")

@router.message(F.text == "🔙 Назад")
async def handle_back(message: Message):
    await start_handler(message)
