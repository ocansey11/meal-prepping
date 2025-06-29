import os
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load environment variables
load_dotenv("app/.env")

def check_spreadsheet():
    try:
        spreadsheet_id = os.getenv("SPREADSHEET_ID")
        print(f"Spreadsheet ID: {spreadsheet_id}")
        
        # Load credentials
        creds = service_account.Credentials.from_service_account_file(
            'app/credentials.json',
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        # Build service
        service = build('sheets', 'v4', credentials=creds)
        
        # Get sheet data
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range="Sheet1!A:F"
        ).execute()
        
        values = result.get('values', [])
        
        print(f"\nCurrent spreadsheet contents ({len(values)} rows):")
        print("-" * 50)
        
        if not values:
            print("Spreadsheet is empty")
        else:
            for i, row in enumerate(values):
                print(f"Row {i+1}: {row}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    check_spreadsheet()
