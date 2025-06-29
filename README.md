# 🧾 Receipt OCR Tool

Simple OCR tool to extract ingredients and prices from receipt images, review the data, and send it to your spreadsheet.

---

## ⚙️ What It Does

- Upload a receipt image
- Extract item names, prices, quantities, and purchase date
- Review/edit the extracted data in a table
- Send approved data to Google Sheets

---

## 📁 Project Structure

```
meal-prepping/
├── app/
│   ├── main.py              # FastAPI app: upload, process, submit routes
│   ├── agent/
│   │   ├── ocr.py           # OCR wrapper to extract text from images
│   │   ├── parser.py        # Parse OCR text into structured data
│   │   └── infer.py         # Clean up quantities and prices
│   ├── services/
│   │   └── sheets.py        # Google Sheets integration
│   ├── templates/
│   │   └── review.html      # Review page with editable table
│   └── static/
│       └── styles.css       # Basic styling
├── tests/
│   └── test_parser.py       # Unit tests
├── requirements.txt         # Dependencies
└── README.md
```
## 🔄 How It Works

```
[1] Upload receipt image
        ↓
[2] OCR extracts text
        ↓
[3] Parse into structured data
        ↓
[4] Review/edit in table
        ↓
[5] Send to Google Sheets
```

## 📊 Output Example

```json
[
  {
    "Date": "2025-06-29",
    "Ingredient": "Whole Milk",
    "Quantity": "2 PT",
    "Price": "2.40",
    "Notes": ""
  },
  {
    "Date": "2025-06-29", 
    "Ingredient": "Indomie Noodles",
    "Quantity": "1 pack",
    "Price": "2.00",
    "Notes": ""
  }
]
```


## 📝 Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Google Sheets API**
   - Get `credentials.json` from Google Cloud Console
   - Place in project root

3. **Run the app**
   ```bash
   uvicorn app.main:app --reload
   ```

## 📦 Dependencies

```txt
fastapi
uvicorn
pillow
easyocr
google-api-python-client
google-auth
python-multipart
```


## ✅ Completed Tasks

- ✅ Build /upload and /process routes in main.py
- ✅ Write ocr.py to extract text lines  
- ✅ Write parser.py to extract item, price, quantity from lines
- ✅ Create review.html to show editable rows
- ✅ Write sheets.py to append rows to a Google Sheet

## 🚀 Quick Start

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup Google Sheets**
   - Create a Google Cloud project
   - Enable Google Sheets API
   - Download `credentials.json` and place in project root
   - Update `SPREADSHEET_ID` in `app/services/sheets.py`

3. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

4. **Open browser**
   - Go to `http://localhost:8000`
   - Upload a receipt image
   - Review and edit extracted data
   - Submit to your Google Sheet
