import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timedelta
import pytz
import logging
from config import GOOGLE_SHEET_ID, TIMEZONE, CLIENTS_SHEET_NAME, ADMIN_SHEET_NAME, SLOTS_SHEET_NAME

logging.basicConfig(level=logging.INFO)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_file("key.json", scopes=SCOPES)
client = gspread.authorize(credentials)

spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)
clients_sheet = spreadsheet.worksheet(CLIENTS_SHEET_NAME)
admin_sheet = spreadsheet.worksheet(ADMIN_SHEET_NAME)
slots_sheet = spreadsheet.worksheet(SLOTS_SHEET_NAME)

tz = pytz.timezone(TIMEZONE)

def get_available_slots(day_offset=0):
    target_date = (datetime.now(tz) + timedelta(days=day_offset)).date().isoformat()
    all_records = clients_sheet.get_all_records()
    result = []

    for record in all_records:
        if (
            record.get("дата") == target_date
            and record.get("статус") == "Записан"
        ):
            result.append({
                "дата": record["дата"],
                "время": record["время"],
                "услуга": record["услуга"]
            })

    all_slots = slots_sheet.get_all_records()
    free_slots = []

    for slot in all_slots:
        if slot.get("статус") == "свободно":
            slot_time = slot["время"]
            already_booked = any(s["время"] == slot_time for s in result)
            if not already_booked:
                free_slots.append({
                    "дата": target_date,
                    "время": slot_time,
                    "услуга": "Маникюр"
                })

    return free_slots

def book_slot(telegram_id, name, phone, date, time, service):
    all_rows = clients_sheet.get_all_values()
    header = all_rows[0]
    new_row = [
        telegram_id, name, phone, date, time, service, "0", "Записан", ""
    ]
    clients_sheet.append_row(new_row)
    return {
        "telegram_id": telegram_id,
        "name": name,
        "phone": phone,
        "date": date,
        "time": time,
        "service": service
    }

def get_user_bookings(telegram_id):
    records = clients_sheet.get_all_records()
    return [
        {
            "дата": r["дата"],
            "время": r["время"],
            "услуга": r["услуга"],
            "row_num": idx + 2
        }
        for idx, r in enumerate(records)
        if str(r.get("Telegram ID")) == str(telegram_id) and r.get("статус") == "Записан"
    ]

def cancel_booking_by_row(row_num):
    try:
        row = clients_sheet.row_values(row_num)
        header = clients_sheet.row_values(1)
        data = dict(zip(header, row))

        clients_sheet.update(f"A{row_num}:I{row_num}", [[""] * 9])
        clients_sheet.update_cell(row_num, header.index("статус") + 1, "Отменен")

        return data
    except Exception as e:
        logging.error(f"Cancel error: {e}")
        return None

def add_free_client_entry(name, phone, count, date_str, time_str, service_name="Бесплатное посещение"):
    row = [
        f"Бесплатно ({count})",
        name,
        phone,
        date_str,
        time_str,
        service_name,
        "0",
        "Записан",
        "✅"
    ]
    clients_sheet.append_row(row)
    return True

def get_today_summary():
    today = datetime.now(tz).date().isoformat()
    records = clients_sheet.get_all_records()
    total = 0
    free_count = 0
    for r in records:
        if r.get("дата") == today and r.get("статус") == "Записан":
            if r.get("бесплатно") == "✅":
                free_count += 1
            else:
                try:
                    total += int(r.get("сумма", 0))
                except:
                    continue
    return total, free_count

def set_day_off(date_str):
    all_rows = clients_sheet.get_all_values()
    header = all_rows[0]
    row = [
        "", "Выходной", "", date_str, "", "—", "0", "Скрыто", ""
    ]
    clients_sheet.append_row(row)

def get_admins():
    return [str(row[0]) for row in admin_sheet.get_all_values()[1:]]

def get_templates():
    return [row[0] for row in spreadsheet.worksheet("templates").get_all_values() if row]
