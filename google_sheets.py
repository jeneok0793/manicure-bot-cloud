import gspread
from google.oauth2.service_account import Credentials
from config import SPREADSHEET_ID, GOOGLE_KEY_PATH

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file(GOOGLE_KEY_PATH, scopes=SCOPES)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID)

def get_worksheet(name):
    return sheet.worksheet(name)

def read_cell(sheet_name, cell):
    return get_worksheet(sheet_name).acell(cell).value

def write_cell(sheet_name, cell, value):
    get_worksheet(sheet_name).update_acell(cell, value)

def append_row(sheet_name, row):
    get_worksheet(sheet_name).append_row(row)

def find_row(sheet_name, value):
    worksheet = get_worksheet(sheet_name)
    try:
        cell = worksheet.find(value)
        return worksheet.row_values(cell.row)
    except gspread.exceptions.CellNotFound:
        return None