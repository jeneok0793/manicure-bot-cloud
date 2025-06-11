from aiogram import Router, F, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ADMIN_CHAT_ID
from google_sheets import (
    get_available_slots, book_slot, get_user_bookings,
    cancel_booking_by_row, add_free_client_entry, clients_sheet
)
from keyboards import (
    get_main_keyboard, get_booking_date_keyboard, create_time_service_keyboard,
    get_cancel_confirm_keyboard, get_select_booking_keyboard,
    get_admin_main_keyboard, get_admin_slot_manage_keyboard, notify_admin
)

router = Router()

class BookingStates(StatesGroup):
    choosing_date = State()
    entering_name = State()
    entering_phone = State()
    confirm_booking = State()

class CancellationStates(StatesGroup):
    choosing_booking_to_cancel = State()
    confirming_cancellation = State()

class AdminStates(StatesGroup):
    main_admin_menu = State()
    managing_slot = State()
    entering_slot_to_hide = State()
    entering_slot_to_show = State()
    adding_free_client = State()

@router.message(F.text == "/start")
async def handle_start(message: types.Message, state: FSMContext):
    await state.clear()
    is_admin = str(message.from_user.id) == str(ADMIN_CHAT_ID)
    await message.answer(
        "Привет! 👋 Я бот для записи к мастеру маникюра 💅\n"
        "Воспользуйтесь кнопками ниже, чтобы записаться или посмотреть свои записи.",
        reply_markup=get_main_keyboard(is_admin)
    )

@router.message(F.text == "📝 Записаться")
async def handle_book_appointment(message: types.Message, state: FSMContext):
    await message.answer("Выберите день для записи:", reply_markup=get_booking_date_keyboard())
    await state.set_state(BookingStates.choosing_date)

@router.callback_query(BookingStates.choosing_date, F.data.startswith("select_date_"))
async def process_date_selection(callback_query: types.CallbackQuery, state: FSMContext):
    selected_date_str = callback_query.data.split("_")[2]
    all_available_slots = get_available_slots(day_offset=0)
    available_slots_for_day = [
        s for s in all_available_slots if s["дата"] == selected_date_str
    ]
    if not available_slots_for_day:
        await callback_query.message.edit_text(
            f"❌ На {selected_date_str} нет свободных слотов. Пожалуйста, выберите другую дату.",
            reply_markup=get_booking_date_keyboard()
        )
        await state.set_state(BookingStates.choosing_date)
    else:
        await state.update_data(selected_date=selected_date_str)
        await callback_query.message.edit_text(
            f"📅 Выбрана дата: *{selected_date_str}*\nВыберите удобное время и услугу:",
            reply_markup=create_time_service_keyboard(available_slots_for_day),
            parse_mode=ParseMode.MARKDOWN_V2
        )
        await state.set_state(BookingStates.confirm_booking)
    await callback_query.answer()

@router.callback_query(BookingStates.confirm_booking, F.data.startswith("book_"))
async def process_time_service_selection(callback_query: types.CallbackQuery, state: FSMContext):
    parts = callback_query.data.split("_")
    booking_date = parts[1]
    booking_time = parts[2]
    booking_service = parts[3]
    await state.update_data(
        booking_date=booking_date,
        booking_time=booking_time,
        booking_service=booking_service
    )
    await callback_query.message.edit_text(
        f"Вы выбрали: *{booking_date}* в *{booking_time}* на услугу *{booking_service}*.\n"
        "Пожалуйста, введите ваше *Имя* для записи:",
        parse_mode=ParseMode.MARKDOWN_V2
    )
    await state.set_state(BookingStates.entering_name)
    await callback_query.answer()

@router.message(BookingStates.entering_name)
async def process_name_input(message: types.Message, state: FSMContext):
    user_name = message.text
    await state.update_data(user_name=user_name)
    await message.answer(
        "Отлично! Теперь, пожалуйста, введите ваш *номер телефона* для связи (например, +373xxxxxxxxx):",
        parse_mode=ParseMode.MARKDOWN_V2
    )
    await state.set_state(BookingStates.entering_phone)

@router.message(BookingStates.entering_phone)
async def process_phone_input(message: types.Message, state: FSMContext):
    user_phone = message.text
    if not user_phone.strip():
        await message.answer("Номер телефона не может быть пустым. Пожалуйста, введите ваш номер телефона:")
        return

    data = await state.get_data()
    booking_date = data.get("booking_date")
    booking_time = data.get("booking_time")
    booking_service = data.get("booking_service")
    user_name = data.get("user_name")
    telegram_id = str(message.from_user.id)

    booked_info = book_slot(telegram_id, user_name, user_phone, booking_date, booking_time, booking_service)

    if booked_info:
        await message.answer(
            f"✅ *Успешно записано!* Вы записаны на:\n"
            f"📅 Дата: *{booking_date}*\n"
            f"🕒 Время: *{booking_time}*\n"
            f"💅 Услуга: *{booking_service}*\n"
            f"До встречи! 🌸",
            parse_mode=ParseMode.MARKDOWN_V2,
            reply_markup=get_main_keyboard(str(message.from_user.id) == str(ADMIN_CHAT_ID))
        )
        admin_message = (
            f"📌 *НОВАЯ ЗАПИСЬ!*\n"
            f"🧑‍💻 Клиент: {user_name}\n"
            f"📞 Телефон: `{user_phone}`\n"
            f"🆔 Telegram ID: `{telegram_id}`\n"
            f"📅 Дата: *{booking_date}*\n"
            f"🕒 Время: *{booking_time}*\n"
            f"💅 Услуга: *{booking_service}*"
        )
        await notify_admin(message.bot, admin_message)
    else:
        await message.answer(
            "Извините, не удалось записать вас. Возможно, слот уже занят или произошла ошибка.\n"
            "Пожалуйста, попробуйте снова или выберите другое время.",
            reply_markup=get_main_keyboard(str(message.from_user.id) == str(ADMIN_CHAT_ID))
        )
    await state.clear()
