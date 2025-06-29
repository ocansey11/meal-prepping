from fastapi import FastAPI, File, UploadFile, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
import json
from datetime import datetime
from typing import List, Dict
import os
from dotenv import load_dotenv

from .agent.vlm import check_api_access, init_openai_client, extract_with_gpt4v
from .services.sheets import append_to_sheet

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

app = FastAPI(title="Receipt OCR Tool")

# Setup templates and static files
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Store extracted data temporarily (in production, use database/session)
extracted_data = []
extraction_metadata = {"method": "unknown", "success": True, "error": None}
uploaded_filename = "unknown_file"

def load_upload_history():
    """Load upload history from JSON file"""
    try:
        if os.path.exists("upload_history.json"):
            with open("upload_history.json", "r") as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error loading history: {e}")
        return []

def save_upload_history(history):
    """Save upload history to JSON file"""
    try:
        with open("upload_history.json", "w") as f:
            json.dump(history, f, indent=2)
    except Exception as e:
        print(f"Error saving history: {e}")

def add_to_history(filename, method, items_count):
    """Add a new upload to history"""
    history = load_upload_history()
    
    new_entry = {
        "filename": filename,
        "method": method,
        "timestamp": datetime.now().isoformat(),
        "items_count": items_count
    }
    
    history.append(new_entry)
    
    # Keep only last 50 uploads
    if len(history) > 50:
        history = history[-50:]
    
    save_upload_history(history)
    return new_entry

@app.get("/", response_class=HTMLResponse)
async def upload_page(request: Request):
    """Upload page for receipt images"""
    return templates.TemplateResponse("upload.html", {"request": request})

@app.post("/upload")
async def upload_receipt(file: UploadFile = File(...), method: str = Form(...)):
    """Handle receipt image upload and VLM processing"""
    global extracted_data, extraction_metadata, uploaded_filename
    
    # Store the filename for history tracking
    uploaded_filename = file.filename or "unknown"
    
    # Save uploaded file temporarily
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    try:
        # Use GPT-4V for extraction
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            extraction_metadata = {
                "method": "vlm", 
                "success": False, 
                "error": "OpenAI API key not configured"
            }
            extracted_data = []
        else:
            # Initialize OpenAI client and extract with GPT-4V
            init_openai_client(api_key)
            extracted_data = extract_with_gpt4v(temp_path)
            
            if not extracted_data:
                extraction_metadata = {
                    "method": "vlm", 
                    "success": False, 
                    "error": "VLM extraction failed - no items found"
                }
            else:
                extraction_metadata = {
                    "method": "vlm", 
                    "success": True, 
                    "error": None
                }
        
        # Clean up temp file
        os.remove(temp_path)
        
        # Redirect to review page
        return RedirectResponse(url="/review", status_code=303)
        
    except Exception as e:
        os.remove(temp_path) if os.path.exists(temp_path) else None
        return {"error": f"Processing failed: {str(e)}"}

@app.get("/review", response_class=HTMLResponse)
async def review_page(request: Request):
    """Review page with editable table of extracted data"""
    return templates.TemplateResponse("review.html", {
        "request": request, 
        "data": extracted_data,
        "metadata": extraction_metadata
    })

@app.post("/submit")
async def submit_to_sheets(items: str = Form(...)):
    """Submit approved data to Google Sheets"""
    try:
        # Parse the JSON string from form
        approved_items = json.loads(items)
        
        # Send to Google Sheets with filename for history tracking
        result = append_to_sheet(approved_items, uploaded_filename)
        
        if result.get('success'):
            # Add to history
            add_to_history(uploaded_filename, extraction_metadata.get("method", "unknown"), len(approved_items))
            
            # Redirect to history page instead of showing success message
            return RedirectResponse(url="/history", status_code=303)
        else:
            return {"error": f"Failed to submit: {result.get('error', 'Unknown error')}"}
        
    except Exception as e:
        return {"error": f"Failed to submit: {str(e)}"}

@app.get("/api/data")
async def get_extracted_data():
    """API endpoint to get current extracted data"""
    return {
        "data": extracted_data,
        "metadata": extraction_metadata
    }

@app.post("/test-openai")
async def test_openai_key(api_key: str = Form(...)):
    """Test OpenAI API key and check available models"""
    try:
        result = check_api_access(api_key)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/history", response_class=HTMLResponse)
async def history_page(request: Request):
    """History page showing upload history"""
    history = load_upload_history()
    last_upload = history[-1] if history else None
    
    # Format timestamp for display
    if last_upload and last_upload.get("timestamp"):
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(last_upload["timestamp"])
            last_upload["formatted_timestamp"] = dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            last_upload["formatted_timestamp"] = last_upload["timestamp"]
    
    return templates.TemplateResponse("history.html", {
        "request": request,
        "last_upload": last_upload,
        "spreadsheet_id": os.getenv("SPREADSHEET_ID"),
        "all_history": history[-10:]  # Show last 10 uploads
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
