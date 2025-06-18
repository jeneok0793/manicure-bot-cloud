import gspread
from google.oauth2.service_account import Credentials
from config import SPREADSHEET_ID, GOOGLE_KEY_PATH

def get_service():
    credentials = Credentials.from_service_account_file(
        GOOGLE_KEY_PATH,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    client = gspread.authorize(credentials)
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    return spreadsheet
