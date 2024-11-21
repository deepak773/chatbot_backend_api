import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import sqlite3
import pandas as pd
from sqlalchemy import create_engine

# Define the required scopes
SCOPE = [
    'https://www.googleapis.com/auth/drive.metadata.readonly',
    'https://www.googleapis.com/auth/spreadsheets.readonly'
]

def list_sheets(SERVICE_ACCOUNT_FILE, FOLDER_ID):
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPE)
    client = gspread.authorize(creds)
    drive_service = build('drive', 'v3', credentials=creds)
    query = f"'{FOLDER_ID}' in parents and mimeType='application/vnd.google-apps.spreadsheet'"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    return files

def get_worksheet_data(SERVICE_ACCOUNT_FILE, SPREADSHEET_ID, worksheet_name):
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPE)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SPREADSHEET_ID)
    worksheet = client.open_by_key(SPREADSHEET_ID).worksheet(worksheet_name)
    data = worksheet.get_all_values()
    df = pd.DataFrame(data)
    return df

def list_tables(db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()
    print("Tables in the database:")
    for table in tables:
        print(table[0])  
    conn.close()

def ingest_data(sheet_id, eligible_worksheets, DATABASE_URL):
    for worksheet in eligible_worksheets:
        data = get_worksheet_data(sheet_id, worksheet)
        worksheet = worksheet.replace(" ","_")
        sheet_name = sheet_name.replace(" ","_")
        table_name = sheet_name+'__'+worksheet
        engine = create_engine(DATABASE_URL)
        data.to_sql(table_name, engine, if_exists="replace", index=False)
        print(f"Table '{table_name}' created successfully!")


