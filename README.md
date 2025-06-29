# 🧾 Ingredient Logger AI Agent

A lightweight vision-powered tool to extract ingredients and prices from receipt images, review/edit the data, and push it to a structured food prep sheet (Google Sheets or Excel).

---

## ⚙️ Project Goals

- Upload a receipt image (e.g. from Lidl)
- Extract item names, prices, quantities (where possible), and the purchase date
- Show results in an editable table on a review screen
- Push approved items to Google Sheets (or Excel backup)

---

## 📁 Project Structure

ingredient-logger/
├── app/
│ ├── main.py # FastAPI app: routes for upload, process, submit
│ │
│ ├── agent/
│ │ ├── ocr.py # Tesseract/EasyOCR wrapper: extract raw lines from image
│ │ ├── parser.py # Line filtering + parsing into item dicts
│ │ └── infer.py # Infer quantity, category, shelf life (if possible)
│ │
│ ├── services/
│ │ └── sheets.py # Google Sheets or MCP integration logic
│ │
│ ├── templates/
│ │ └── review.html # Renders editable table of extracted items
│ │
│ └── static/
│ └── styles.css # Optional minimal CSS
│
├── tests/
│ └── test_parser.py # Unit tests for OCR and parsing logic
│
├── requirements.txt # FastAPI, OCR, Sheets API
└── README.md # You're here.

yaml
## 🧠 App Flow

```text
[1] User uploads receipt image
        ↓
[2] /process route:
    - OCR reads image
    - Parser filters for item lines
    - Quantity/price inferred
        ↓
[3] /review page:
    - Shows editable table of extracted items
    - User approves or edits
        ↓
[4] /submit route:
    - Sends approved items to Google Sheets
```


Example Output

[
  {
    
  "Date": "2025-06-29",
  "Ingredient": "Whole Milk",
  "Quantity": "2 PT",
  "Notes": "",
  "Price": "2.4",
  },
  {
    
  "Date": "2025-06-29",
  "Ingredient": "Indomie Milk",
  "Quantity": "1pack",
  "Notes": "",
  "Price": "2.0",
  },
]


🧾 Google Sheets Setup
- Use Google Sheets API
- Authenticate using credentials.json


Dependencies (requirements.txt):
txt
Copy
Edit
fastapi
uvicorn
pillow
easyocr
openai           # optional for VLM
google-api-python-client
google-auth
python-multipart


Copilot To-Do Checklist
 Build /upload and /process routes in main.py

 Write ocr.py to extract text lines

 Write parser.py to extract item, price, quantity from lines

 Create review.html to show editable rows

 Write sheets.py to append rows to a Google Sheet
