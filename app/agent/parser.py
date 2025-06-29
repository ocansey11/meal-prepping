import re
from datetime import datetime
from typing import List, Dict

def parse_receipt_lines(text_lines: List[str]) -> List[Dict]:
    """
    Parse OCR text lines into structured ingredient data
    
    Args:
        text_lines: List of text lines from OCR
        
    Returns:
        List of dictionaries with ingredient data
    """
    items = []
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    for line in text_lines:
        # Skip empty lines and common receipt headers/footers
        if not line.strip() or is_header_footer(line):
            continue
            
        # Try to extract item data from line
        item_data = extract_item_from_line(line, current_date)
        if item_data:
            items.append(item_data)
    
    return items

def extract_item_from_line(line: str, date: str) -> Dict:
    """
    Extract item name, quantity, and price from a single line
    """
    line = line.strip()
    
    # Pattern to match price at end of line (£1.99, $2.50, 1.99, etc.)
    price_pattern = r'[\£\$]?(\d+\.\d{2})$'
    price_match = re.search(price_pattern, line)
    
    if not price_match:
        return None
    
    price = price_match.group(1)
    
    # Remove price from line to get item name
    item_line = line[:price_match.start()].strip()
    
    # Try to extract quantity (common patterns)
    quantity = extract_quantity(item_line)
    
    # Clean up item name
    item_name = clean_item_name(item_line, quantity)
    
    return {
        "Date": date,
        "Ingredient": item_name,
        "Quantity": quantity,
        "Price": price,
        "Notes": ""
    }

def extract_quantity(text: str) -> str:
    """
    Extract quantity from item text
    """
    # Common quantity patterns
    qty_patterns = [
        r'(\d+)\s*x\s*',       # "2 x", "3x"
        r'(\d+)\s*(kg|g|lb|oz|pt|l|ml)', # "2 kg", "500g", "2 PT"
        r'(\d+)\s*(pack|bag|bottle|can)', # "1 pack", "2 bottles"
    ]
    
    for pattern in qty_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0).strip()
    
    return "1"  # Default quantity

def clean_item_name(text: str, quantity: str) -> str:
    """
    Clean up item name by removing quantity and extra characters
    """
    # Remove quantity from text
    clean_text = text.replace(quantity, "").strip()
    
    # Remove common prefixes/suffixes
    clean_text = re.sub(r'^(organic|fresh|free range|)\s*', '', clean_text, flags=re.IGNORECASE)
    clean_text = re.sub(r'\s*(ea|each)$', '', clean_text, flags=re.IGNORECASE)
    
    # Capitalize properly
    clean_text = clean_text.title()
    
    return clean_text.strip()

def is_header_footer(line: str) -> bool:
    """
    Check if line is likely a header/footer and should be skipped
    """
    skip_keywords = [
        'receipt', 'total', 'subtotal', 'tax', 'vat', 'change', 'cash', 'card',
        'thank you', 'visit', 'store', 'phone', 'address', 'date', 'time',
        'cashier', 'till', 'transaction', 'balance', 'discount'
    ]
    
    line_lower = line.lower()
    return any(keyword in line_lower for keyword in skip_keywords)
