from googleapiclient.discovery import build
from google.oauth2 import service_account

SERVICE_ACCOUNT_FILE = 'keys.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

creds = None
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# ID Spreadsheet
SPREADSHEET_ID = '1N1KeSDN02a1EmbeU8GLpL87s13qBuWaDToQzrZAIdP0'

service = build('sheets', 'v4', credentials=creds)


def update_sheet(aoa):
    # Call Sheets API
    sheet = service.spreadsheets()
    request = sheet.values().append(spreadsheetId=SPREADSHEET_ID, range="Bot-1!A1",
                                   valueInputOption="USER_ENTERED", body={"values":aoa}).execute()
    # append_request = sheet.values().append_rows()

    print(request)