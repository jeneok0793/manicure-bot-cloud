# handlers.py
# Обновление интерфейса от 14 июня

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command
from google_sheets import get_available_slots, book_slot, cancel_booking, get_user_bookings, get_todays_records, get_discount_status, get_total_visits, get_admin_stats, add_free_client, get_all_clients, update_setting, get_settings
from config import ADMIN_CHAT_ID

router = Router()

# FSM для отмены
class CancelState(StatesGroup):
    waiting_confirmation = State()

# Главная клавиатура клиента
def main_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📅 Записаться")],
        [KeyboardButton(text="🗓 Мои записи"), KeyboardButton(text="❌ Отменить запись")],
        [KeyboardButton(text="ℹ️ О мастере")]
    ], resize_keyboard=True)

# Админская клавиатура
def admin_keyboard():
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text="📊 Записи на сегодня"), KeyboardButton(text="💰 Итоги дня")],
        [KeyboardButton(text="🎁 Добавить бесплатного клиента")],
        [KeyboardButton(text="📨 Рассылка"), KeyboardButton(text="⚙️ Настройки")]
    ], resize_keyboard=True)

# Приветствие
@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    if str(message.from_user.id) == str(ADMIN_CHAT_ID):
        await message.answer("Добро пожаловать, админ!", reply_markup=admin_keyboard())
    else:
        await message.answer(
            "👋 Привет! Я бот записи на маникюр 💅

"
            "С моей помощью ты сможешь:
"
            "🗓 выбрать удобное время
"
            "⏰ получать напоминания
"
            "📍 узнать адрес и цены

"
            "Жми кнопку ниже 👇",
            reply_markup=main_keyboard()
        )

# Запись
@router.message(F.text == "📅 Записаться")
async def choose_date(message: Message, state: FSMContext):
    slots = get_available_slots()
    if not slots:
        await message.answer("На ближайшие дни мест нет. Хотите оставить заявку на первую свободную дату?", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да, хочу", callback_data="waitlist_yes")],
            [InlineKeyboardButton(text="❌ Нет, позже", callback_data="waitlist_no")]
        ]))
        return
    text = "📅 Доступные слоты:

"
    for date, times in slots.items():
        text += f"<b>{date}</b>:
" + ", ".join(times) + "

"
    await message.answer(text, parse_mode="HTML")

# Просмотр записей
@router.message(F.text == "🗓 Мои записи")
async def view_bookings(message: Message, state: FSMContext):
    bookings = get_user_bookings(message.from_user.id)
    if not bookings:
        await message.answer("У вас пока нет записей.")
        return
    text = "📌 Ваши записи:

"
    for b in bookings:
        text += f"{b['date']} в {b['time']} — {b['service']} ({b['price']} лей)
"
    visits = get_total_visits(message.from_user.id)
    to_discount = 6 - (visits % 6)
    if to_discount == 1:
        text += "
🎉 Следующая процедура со скидкой 10%!"
    else:
        text += f"
💡 У вас уже {visits % 6} процедур — осталось {to_discount} до скидки 10%!"
    await message.answer(text)

# Отмена записи
@router.message(F.text == "❌ Отменить запись")
async def cancel_booking_start(message: Message, state: FSMContext):
    bookings = get_user_bookings(message.from_user.id)
    if not bookings:
        await message.answer("У вас нет активных записей.")
        return
    b = bookings[-1]
    await state.set_state(CancelState.waiting_confirmation)
    await message.answer(
        f"Вы хотите отменить запись:
📅 {b['date']} в {b['time']}

Подтвердите действие:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да, отменить", callback_data="cancel_yes")],
            [InlineKeyboardButton(text="🔁 Перезаписаться", callback_data="reschedule")],
            [InlineKeyboardButton(text="↩️ Назад", callback_data="cancel_no")]
        ])
    )

@router.callback_query(CancelState.waiting_confirmation, F.data == "cancel_yes")
async def confirm_cancel(call: CallbackQuery, state: FSMContext):
    cancel_booking(call.from_user.id)
    await call.message.edit_text("Запись отменена.")
    await state.clear()

@router.callback_query(CancelState.waiting_confirmation, F.data == "reschedule")
async def reschedule(call: CallbackQuery, state: FSMContext):
    cancel_booking(call.from_user.id)
    await call.message.edit_text("Хорошо, давайте перезапишемся!")
    await state.clear()
    await choose_date(call.message, state)

@router.callback_query(CancelState.waiting_confirmation, F.data == "cancel_no")
async def cancel_back(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Действие отменено.")
    await state.clear()

# О мастере
@router.message(F.text == "ℹ️ О мастере")
async def about_master(message: Message, state: FSMContext):
    settings = get_settings()
    text = f"📍 Адрес: {settings['address']}

💅 Актуальный прайс — мастер Евгения:

"
    text += (
        "💎 Наращивание ногтей — 280 лей
"
        "💎 Коррекция ногтей — 240 лей
"
        "💅 Покрытие гель-лаком — 210 лей
"
        "🦶 Педикюр — 250 лей
"
        "🦶 Педикюр + обработка пяточек — 320 лей

"
        "🎁 Каждая 6-я процедура — со скидкой 10% по системе 5+1"
    )
    await message.answer(text)

# Админ
@router.message(F.text == "/admin")
async def admin_panel(message: Message, state: FSMContext):
    if str(message.from_user.id) != str(ADMIN_CHAT_ID):
        await message.answer("Нет доступа.")
        return
    await message.answer("Панель администратора:", reply_markup=admin_keyboard())

# Остальные функции админа (сегодняшние записи, итоги, рассылка, добавление клиента и т.п.)
# вставляются ниже — мы продолжим их при необходимости