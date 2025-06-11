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
