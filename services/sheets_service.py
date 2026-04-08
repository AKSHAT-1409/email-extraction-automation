import gspread
from google.oauth2.service_account import Credentials

from config import SHEET_NAME


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def get_sheet():
    creds = Credentials.from_service_account_file(
        "service_account.json", scopes=SCOPES
    )
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key("1MbD9crqdRiQQ_35lPq9J-m8qXUcn4-_hC-SnXMoxZG4")
    
    try:
        sheet = spreadsheet.worksheet(SHEET_NAME)
    except gspread.exceptions.WorksheetNotFound:
        # Create it if it doesn't exist
        sheet = spreadsheet.add_worksheet(title=SHEET_NAME, rows=1000, cols=20)
        
    return sheet


def append_to_sheet(data):
    try:
        sheet = get_sheet()

        row = [
            data.get("extracted_at", ""),
            data.get("source_email", ""),
            data.get("job_title", ""),
            data.get("job_id", ""),
            data.get("facility_name", ""),
            data.get("location", ""),
            data.get("job_type", ""),
            data.get("shift", ""),
            data.get("duration", ""),
            data.get("start_date", ""),
            data.get("hourly_rate", ""),
            data.get("experience_required", ""),
            data.get("certifications", "")
        ]

        sheet.append_row(row)

        print("[SHEET] Data added successfully")

    except Exception as e:
        print(f"[SHEET ERROR] {str(e)}")


def initialize_sheet():
    sheet = get_sheet()

    headers = [
        "extracted_at",
        "source_email",
        "job_title",
        "job_id",
        "facility_name",
        "location",
        "job_type",
        "shift",
        "duration",
        "start_date",
        "hourly_rate",
        "experience_required",
        "certifications"
    ]

    existing = sheet.get_all_values()

    if not existing:
        sheet.append_row(headers)
        print("[SHEET] Headers added")