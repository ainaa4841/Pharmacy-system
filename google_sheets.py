import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import json
import streamlit as st
import os
import mimetypes
from googleapiclient.http import MediaFileUpload

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
service_account_info = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
client = gspread.authorize(creds)
spreadsheet = client.open_by_key(st.secrets["SPREADSHEET_ID"])
FOLDER_ID = st.secrets["FOLDER_ID"]

def generate_next_id(sheet, col_name):
    records = spreadsheet.worksheet(sheet).get_all_records()
    if not records: return 1
    return int(records[-1][col_name]) + 1

def save_customer(data):
    ws = spreadsheet.worksheet("Customers")
    cid = generate_next_id("Customers", "customerID")
    ws.append_row([cid] + data)
    return cid

def save_appointment(data, referral_path=None):
    worksheet = spreadsheet.worksheet("Appointments")
    appointment_id = generate_next_id("Appointments", "appointmentID")
    if referral_path is None:
        referral_path = ""
    worksheet.append_row([appointment_id] + data + [referral_path])  # Add referral path to appointment
    remove_schedule_slot(data[1], data[2])  # data[1] = date, data[2] = time

def get_appointments():
    ws = spreadsheet.worksheet("Appointments")
    return ws.get_all_records()

def update_schedule(date, time):
    ws = spreadsheet.worksheet("Schedules")
    ws.append_row([date, time])

def get_pharmacist_schedule():
    return spreadsheet.worksheet("Schedules").get_all_records()

def update_appointment_status(appointment_id, new_status, new_date=None, new_time=None):
    worksheet = spreadsheet.worksheet("Appointments")
    records = worksheet.get_all_records()
    for idx, record in enumerate(records, start=2):  # Row 2 = data starts
        if str(record["appointmentID"]) == str(appointment_id):
            if new_status == "Cancelled":
                worksheet.update_acell(f"D{idx}", "Cancelled")
                restore_schedule_slot(record["appointmentDate"], record["appointmentTime"])
            elif new_status == "Rescheduled":
                old_date, old_time = record["appointmentDate"], record["appointmentTime"]
                worksheet.update_acell(f"B{idx}", new_date)
                worksheet.update_acell(f"C{idx}", new_time)
                worksheet.update_acell(f"D{idx}", "Pending Confirmation")
                restore_schedule_slot(old_date, old_time)
                remove_schedule_slot(new_date, new_time)
            else:
                worksheet.update_acell(f"D{idx}", new_status)
            break

def
