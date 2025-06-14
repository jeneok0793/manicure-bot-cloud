import gspread
from google.oauth2.service_account import Credentials
from config import SERVICE_ACCOUNT_FILE, SPREADSHEET_ID

scope = ["https://www.googleapis.com/auth/spreadsheets"]

try:
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID)
except Exception as e:
    import sys
    print("❌ Google Sheets ERROR:", e, file=sys.stderr)
    raise

def get_worksheet(name):
    return sheet.worksheet(name)
