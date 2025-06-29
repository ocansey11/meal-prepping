from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json
import os
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Google Sheets configuration
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
RANGE_NAME = "Sheet1!A:F"  # Matches existing format: Date, Ingredient, Meal, Shelf Life, Price, Quantity

def append_to_sheet(items: List[Dict], source_filename: str = "unknown") -> dict:
    """
    Append items to Google Sheets
    
    Args:
        items: List of dictionaries with ingredient data
        
    Returns:
        Result dictionary with success/error info
    """
    try:
        print(f"DEBUG: Attempting to append {len(items)} items to sheet")
        print(f"DEBUG: Spreadsheet ID from env: {SPREADSHEET_ID}")
        print(f"DEBUG: Source filename: {source_filename}")
        print(f"DEBUG: Items data: {items}")
        
        # Check if spreadsheet ID is configured
        if not SPREADSHEET_ID or SPREADSHEET_ID == "your_google_sheets_id_here":
            return {
                'success': False,
                'error': f'Spreadsheet ID not configured. Current value: {SPREADSHEET_ID}'
            }
        
        # Load credentials
        creds = load_credentials()
        
        # Build the service
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        
        # Prepare data for sheets (convert dict to rows)
        from datetime import datetime
        upload_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        values = []
        for item in items:
            row = [
                item.get('Date', ''),
                item.get('Ingredient', ''),
                '',  # Meal column - blank
                '',  # Shelf Life column - blank  
                item.get('Price', ''),
                item.get('Quantity', '')
            ]
            values.append(row)
        
        print(f"DEBUG: Prepared values: {values}")
        
        # Prepare the request body
        body = {
            'values': values
        }
        
        # Execute the request
        result = sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption='RAW',
            body=body
        ).execute()
        
        print(f"DEBUG: Sheets API result: {result}")
        
        return {
            'success': True,
            'updated_rows': result.get('updates', {}).get('updatedRows', 0)
        }
        
    except Exception as e:
        print(f"DEBUG: Sheets error: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def load_credentials():
    """
    Load Google Sheets API credentials
    """
    try:
        # Try to load service account credentials from app directory
        creds_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "app/credentials.json")
        print(f"DEBUG: Looking for credentials at: {creds_path}")
        
        creds = service_account.Credentials.from_service_account_file(
            creds_path,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        print("DEBUG: Credentials loaded successfully")
        return creds
    except Exception as e:
        print(f"DEBUG: Failed to load credentials: {e}")
        raise Exception(f"Failed to load credentials: {e}")

def create_headers_if_needed():
    """
    Create header row if the sheet is empty
    """
    try:
        creds = load_credentials()
        service = build('sheets', 'v4', credentials=creds)
        
        # Check if first row has headers
        result = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range="Sheet1!A1:F1"  # Updated range
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            # Add headers
            headers = [['Date', 'Ingredient', 'Quantity', 'Price', 'Notes', 'Upload History']]
            body = {'values': headers}
            
            service.spreadsheets().values().update(
                spreadsheetId=SPREADSHEET_ID,
                range="Sheet1!A1:F1",  # Updated range for new column
                valueInputOption='RAW',
                body=body
            ).execute()
            
            return "Headers created"
        
        return "Headers exist"
        
    except Exception as e:
        return f"Error checking/creating headers: {e}"
