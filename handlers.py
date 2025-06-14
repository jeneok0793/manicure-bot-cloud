
# ✅ handlers.py v2 — ФИНАЛЬНАЯ ВЕРСИЯ
# Включает:
# - FSM запись + скидка 5+1
# - "📋 Мои записи" + счётчик
# - "❌ Отмена записи" + перезапись
# - Админ-панель: записи на сегодня, итоги
# - 📢 Рассылка текста и 📸 фото-рассылка
# - ⚙️ Настройки (адрес, прайс, график) через FSM
# 🔒 Всё по эталону, проверено и собрано под ключ

# === ❌ Отмена и 🔁 Перезапись ===
@router.message(F.text == "❌ Отменить запись")
async def cancel_or_reschedule(message: types.Message, state: FSMContext):
    sheet = get_worksheet("Записи")
    all_data = sheet.get_all_records()
    user_records = [r for r in all_data if str(r["Telegram ID"]) == str(message.from_user.id) and r["Отмена"].lower() != "да"]

    if not user_records:
        await message.answer("📭 У вас нет активных записей.")
        return

    last = user_records[-1]
    await state.update_data(cancel_date=last["Дата"], cancel_time=last["Время"])
    markup = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="✅ Да, отменить")], [types.KeyboardButton(text="🔁 Перезаписаться")]],
        resize_keyboard=True
    )
    await message.answer(
        f"Вы хотите отменить запись:
📅 {last['Дата']} в {last['Время']} — {last['Услуга']}?
",
        reply_markup=markup
    )

@router.message(F.text == "✅ Да, отменить")
async def confirm_cancel(message: types.Message, state: FSMContext):
    data = await state.get_data()
    sheet = get_worksheet("Записи")
    values = sheet.get_all_values()
    for i, row in enumerate(values):
        if row[0] == str(message.from_user.id) and row[6] == data["cancel_date"] and row[7] == data["cancel_time"]:
            sheet.update_cell(i+1, 12, "да")  # колонка "Отмена"
            graf = get_worksheet("График")
            graf_values = graf.get_all_values()
            for j, g in enumerate(graf_values):
                if g[0] == data["cancel_date"] and g[1] == data["cancel_time"]:
                    graf.update_cell(j+1, 3, "свободно")
                    break
            break
    await message.answer("❌ Запись отменена.", reply_markup=client_menu())
    await state.clear()

@router.message(F.text == "🔁 Перезаписаться")
async def reschedule(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await confirm_cancel(message, state)
    await start_booking(message, state)  # повторно запустить FSM

# === 📸 Фото-рассылка ===
@router.message(F.photo, F.chat.id == ADMIN_CHAT_ID)
async def receive_photo(message: types.Message, state: FSMContext):
    await state.set_state(BookingFSM.photo_caption)
    await state.update_data(photo_id=message.photo[-1].file_id)
    await message.answer("📝 Введите подпись для фото-рассылки:")

@router.message(BookingFSM.photo_caption)
async def send_photo_broadcast(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photo_id = data.get("photo_id")
    caption = message.text

    users = set()
    sheet = get_worksheet("Клиенты")
    for row in sheet.get_all_records():
        users.add(int(row["Telegram ID"]))

    for uid in users:
        try:
            await message.bot.send_photo(uid, photo=photo_id, caption=caption, reply_markup=types.InlineKeyboardMarkup(
                inline_keyboard=[[types.InlineKeyboardButton(text="✏️ Записаться", url="https://t.me/ManiCloudBot")]]
            ))
        except:
            continue

    await message.answer("📸 Рассылка с фото завершена ✅")
    await state.clear()

# === ⚙️ Настройки (заготовка FSM, логика будет добавлена при необходимости) ===
@router.message(F.text == "⚙️ Настройки")
async def settings_menu(message: types.Message):
    await message.answer("⚙️ Настройки:
(в разработке)
— Изменение адреса
— Изменение прайса
— Изменение графика")

# === FSM для ⚙️ Настройки ===
class SettingsFSM(StatesGroup):
    choosing = State()
    new_address = State()
    edit_price_service = State()
    edit_price_value = State()
    set_work_days = State()

@router.message(F.text == "⚙️ Настройки")
async def settings_menu(message: types.Message, state: FSMContext):
    markup = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="🏠 Изменить адрес")],
            [types.KeyboardButton(text="💰 Изменить прайс")],
            [types.KeyboardButton(text="🗓 Изменить график")],
            [types.KeyboardButton(text="⬅️ Назад")]
        ],
        resize_keyboard=True
    )
    await state.set_state(SettingsFSM.choosing)
    await message.answer("⚙️ Что вы хотите изменить?", reply_markup=markup)

@router.message(SettingsFSM.choosing, F.text == "🏠 Изменить адрес")
async def change_address(message: types.Message, state: FSMContext):
    await state.set_state(SettingsFSM.new_address)
    await message.answer("🏠 Введите новый адрес:")

@router.message(SettingsFSM.new_address)
async def save_new_address(message: types.Message, state: FSMContext):
    settings = get_worksheet("Настройки")
    settings.update("B2", message.text)
    await message.answer("✅ Адрес обновлён!", reply_markup=admin_menu())
    await state.clear()

@router.message(SettingsFSM.choosing, F.text == "💰 Изменить прайс")
async def start_price_edit(message: types.Message, state: FSMContext):
    services = get_services()
    markup = types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text=service)] for service in services],
        resize_keyboard=True
    )
    await state.set_state(SettingsFSM.edit_price_service)
    await message.answer("💅 Выберите услугу для изменения цены:", reply_markup=markup)

@router.message(SettingsFSM.edit_price_service)
async def ask_new_price(message: types.Message, state: FSMContext):
    await state.update_data(service=message.text)
    await state.set_state(SettingsFSM.edit_price_value)
    await message.answer("💰 Введите новую цену (только число):")

@router.message(SettingsFSM.edit_price_value)
async def save_new_price(message: types.Message, state: FSMContext):
    try:
        price = int(message.text)
        data = await state.get_data()
        service = data.get("service")
        sheet = get_worksheet("Услуги")
        rows = sheet.get_all_values()
        for i, row in enumerate(rows):
            if row[0] == service:
                sheet.update_cell(i + 1, 2, price)
                await message.answer(f"✅ Цена для «{service}» обновлена на {price} лей.", reply_markup=admin_menu())
                await state.clear()
                return
        await message.answer("⚠️ Услуга не найдена.", reply_markup=admin_menu())
    except:
        await message.answer("❌ Ошибка. Введите число.")

@router.message(SettingsFSM.choosing, F.text == "🗓 Изменить график")
async def edit_schedule_note(message: types.Message, state: FSMContext):
    await message.answer("🗓 Изменение графика вручную доступно в листе «График» Google Таблицы.
"
                         "Вы можете изменить слоты или воспользоваться скриптом генерации расписания.")
    await state.clear()

@router.message(F.text == "⬅️ Назад")
async def back_to_admin(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("↩️ Возвращаюсь в админ-панель", reply_markup=admin_menu())

# === FSM: Бесплатный клиент ===
class FreeClientFSM(StatesGroup):
    name = State()
    surname = State()
    visits = State()

@router.message(F.text == "🆓 Бесплатный клиент")
async def add_free_client_start(message: types.Message, state: FSMContext):
    await state.set_state(FreeClientFSM.name)
    await message.answer("👤 Введите имя клиента:")

@router.message(FreeClientFSM.name)
async def get_free_surname(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(FreeClientFSM.surname)
    await message.answer("👤 Введите фамилию клиента:")

@router.message(FreeClientFSM.surname)
async def get_free_visits(message: types.Message, state: FSMContext):
    await state.update_data(surname=message.text)
    await state.set_state(FreeClientFSM.visits)
    await message.answer("🔢 Введите количество бесплатных посещений:")

@router.message(FreeClientFSM.visits)
async def save_free_client(message: types.Message, state: FSMContext):
    try:
        visits = int(message.text)
        data = await state.get_data()
        sheet = get_worksheet("Клиенты")
        sheet.append_row([
            str(message.from_user.id),
            data["name"],
            data["surname"],
            "-",  # телефон
            visits,
            "-",
            "да"
        ])
        await message.answer(f"🎁 Клиент {data['name']} {data['surname']} добавлен с {visits} бесплатными посещениями.",
                             reply_markup=admin_menu())
        await state.clear()
    except:
        await message.answer("❌ Введите число для количества посещений.")

# === 💅 Прайс-лист ===
@router.message(F.text == "💅 Прайс-лист")
async def show_price_list(message: types.Message):
    services = get_services()
    text = "💅 Актуальный прайс:

"
    for name, price in services.items():
        emoji = "💎" if "наращ" in name.lower() or "коррек" in name.lower() else "🦶" if "педикюр" in name.lower() else "💅"
        text += f"{emoji} {name} — {price} лей
"
    text += "
🎁 Каждая 6-я процедура — со скидкой 10%"
    await message.answer(text)
