import re
from typing import Dict

def clean_quantity_and_price(item: Dict) -> Dict:
    """
    Clean up and standardize quantity and price fields
    """
    item['Quantity'] = standardize_quantity(item['Quantity'])
    item['Price'] = clean_price(item['Price'])
    item['Ingredient'] = improve_ingredient_name(item['Ingredient'])
    
    return item

def standardize_quantity(quantity: str) -> str:
    """
    Standardize quantity formats
    """
    if not quantity:
        return "1"
    
    # Convert common abbreviations
    replacements = {
        'kg': 'kg',
        'g': 'g', 
        'lb': 'lb',
        'oz': 'oz',
        'pt': 'PT',
        'l': 'L',
        'ml': 'mL',
        'pack': 'pack',
        'bag': 'bag',
        'bottle': 'bottle',
        'can': 'can'
    }
    
    quantity_lower = quantity.lower()
    for old, new in replacements.items():
        quantity_lower = quantity_lower.replace(old, new)
    
    return quantity_lower.strip()

def clean_price(price: str) -> str:
    """
    Clean and format price
    """
    if not price:
        return "0.00"
    
    # Remove currency symbols and extra spaces
    clean_price = re.sub(r'[£$€]', '', price).strip()
    
    # Ensure two decimal places
    try:
        price_float = float(clean_price)
        return f"{price_float:.2f}"
    except ValueError:
        return "0.00"

def improve_ingredient_name(name: str) -> str:
    """
    Improve ingredient name formatting
    """
    if not name:
        return "Unknown Item"
    
    # Common corrections
    corrections = {
        'milk': 'Milk',
        'bread': 'Bread',
        'eggs': 'Eggs',
        'butter': 'Butter',
        'cheese': 'Cheese',
        'chicken': 'Chicken',
        'beef': 'Beef',
        'rice': 'Rice',
        'pasta': 'Pasta'
    }
    
    name_lower = name.lower()
    for key, value in corrections.items():
        if key in name_lower:
            return value
    
    return name.title()
