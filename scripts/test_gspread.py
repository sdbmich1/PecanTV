import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name("pecantv-f585e-6fe7a40a0bea.json", scope)
client = gspread.authorize(creds)

SPREADSHEET_ID = "1ZmUOUX9euUWc6qcLs8H2AFvf3neGEM7uppdKsh0Hj-E"
sheet = client.open_by_key(SPREADSHEET_ID)
print(sheet.worksheets())
