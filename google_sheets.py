import gspread
from google.oauth2.service_account import Credentials
import json
import streamlit as st
import os
import mimetypes
from googleapiclient.http import MediaFileUpload

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

def upload_to_drive(file_path):
    drive_service = build("drive", "v3", credentials=creds)
    file_metadata = {
        "name": os.path.basename(file_path),
        "parents": [st.secrets["FOLDER_ID"]]
    }
    mimetype, _ = mimetypes.guess_type(file_path)
    media = MediaFileUpload(file_path, mimetype=mimetype)
    uploaded_file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()
    return uploaded_file.get("id")

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

def get_pharmacist_schedule():
    return spreadsheet.worksheet("Schedules").get_all_records()

def update_schedule(date, time):
    ws = spreadsheet.worksheet("Schedules")
    ws.append_row([date, time])

def update_appointment_status(appointment_id, new_status, new_date=None, new_time=None):
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet("Appointments")
    records = sheet.get_all_records()
    
    # Map column names to indices (1-based indexing for gspread)
    header = sheet.row_values(1)
    col_index = {name: idx + 1 for idx, name in enumerate(header)}

    for i, row in enumerate(records):
        if str(row.get("appointmentID")) == str(appointment_id):
            row_number = i + 2  # +2 because row 1 is header, and list is 0-indexed

            if new_date:
                sheet.update_cell(row_number, col_index["appointmentDate"], new_date)
            if new_time:
                sheet.update_cell(row_number, col_index["appointmentTime"], new_time)
            if new_status:
                sheet.update_cell(row_number, col_index["appointmentStatus"], new_status)

            break

def get_all_customers():
    return spreadsheet.worksheet("Customers").get_all_records()

def save_report(data):
    ws = spreadsheet.worksheet("Reports")
    rid = generate_next_id("Reports", "reportID")
    ws.append_row([rid] + data)

def remove_schedule_slot(date, time):
    worksheet = spreadsheet.worksheet("Schedules")
    records = worksheet.get_all_records()
    date = str(date).strip().lower()
    time = str(time).strip().lower()

    for idx, record in enumerate(records, start=2):
        rec_date = str(record["availableDate"]).strip().lower()
        rec_time = str(record["availableTimeslot"]).strip().lower()
        if rec_date == date and rec_time == time:
            worksheet.delete_rows(idx)
            return
    print(f"[DEBUG] Slot not found for deletion: {date} - {time}")

def generate_next_id(sheet, col_name):
    records = spreadsheet.worksheet(sheet).get_all_records()
    if not records: return 1
    return int(records[-1][col_name]) + 1
