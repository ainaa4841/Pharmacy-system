import gspread
from google.oauth2.service_account import Credentials
import json
import streamlit as st
import re

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
service_account_info = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
client = gspread.authorize(creds)
spreadsheet = client.open_by_key(st.secrets["SPREADSHEET_ID"])

def register_user(username, password, role, email):
    worksheet = spreadsheet.worksheet("Users")
    worksheet.append_row([username, password, role, email])

def login_user(username, password):
    try:
        # Check Customers sheet
        customer_ws = spreadsheet.worksheet("Customers")
        for customer in customer_ws.get_all_records():
            if customer.get("customerUsername") == username and customer.get("customerPassword") == password:
                return "Customer", customer["customerUsername"], customer["customerEmail"]

        # Check Pharmacist sheet
        pharmacist_ws = spreadsheet.worksheet("Pharmacist")
        for pharm in pharmacist_ws.get_all_records():
            if pharm.get("pharmacistUsername") == username and pharm.get("pharmacistPassword") == password:
                return "Pharmacist", pharm["pharmacistUsername"], pharm["pharmacistEmail"]

        # No match found
        return None, None, None

    except Exception as e:
        print(f"Login error: {e}")
        return None, None, None


def get_customer_id(username):
    worksheet = spreadsheet.worksheet("Customers")
    for record in worksheet.get_all_records():
        if record["customerUsername"] == username:
            return str(record["customerID"])
    return None

ddef check_email_exists(email):
    worksheet = spreadsheet.worksheet("Customers")
    return any(user["customerEmail"] == email for user in worksheet.get_all_records())


def check_password_complexity(password):
    return len(password) >= 8 and re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)
