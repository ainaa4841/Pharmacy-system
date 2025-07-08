import gspread
from google.oauth2.service_account import Credentials
import json
import streamlit as st
# Setup Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
service_account_info = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
client = gspread.authorize(creds)
spreadsheet = client.open_by_key(st.secrets["SPREADSHEET_ID"])
def save_customer(data):
    ws = spreadsheet.worksheet("Customers")
    cid = generate_next_id("Customers", "customerID")
    ws.append_row([cid] + data)
    return cid

def register_user(username, password, email):
    worksheet = spreadsheet.worksheet("Customers")  # Assuming registration is done in Customers
    worksheet.append_row([username, password, email])  # Adjust based on your columns

def login_user(username, password):
    worksheet = spreadsheet.worksheet("Customers")  # Check in Customers
    for user in worksheet.get_all_records():
        if user["customerUsername"] == username and user["customerPassword"] == password:
            return user["customerEmail"]  # Return email if credentials are valid
    # Check for Pharmacist
    worksheet = spreadsheet.worksheet("Pharmacist")  # Assuming Pharmacist data is in a separate sheet
    for user in worksheet.get_all_records():
        if user["pharmacistID"] == username and user["pharmacistPassword"] == password:
            return user["pharmacistEmail"]  # Return email if credentials are valid
    return None  # Return None if no valid credentials found

def get_customer_id(username):
    worksheet = spreadsheet.worksheet("Customers")
    for record in worksheet.get_all_records():
        if record["customerUsername"] == username:
            return str(record["customerID"])
    return None

def check_email_exists(email):
    worksheet = spreadsheet.worksheet("Customers")
    return any(user["customerEmail"] == email for user in worksheet.get_all_records())

def check_password_complexity(password):
    return len(password) >= 8 and re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)

def generate_next_id(sheet, col_name):
    records = spreadsheet.worksheet(sheet).get_all_records()
    if not records: return 1
    return int(records[-1][col_name]) + 1
def update_appointment_status(appointment_id, new_status, new_date=None, new_time=None):
    # Implementation for updating appointment status
    pass
