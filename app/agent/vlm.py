import openai
import base64
from PIL import Image
import json
from typing import List, Dict, Optional
import os
from datetime import datetime

# Initialize OpenAI client
client = None

def init_openai_client(api_key: str):
    """Initialize OpenAI client with API key"""
    global client
    client = openai.OpenAI(api_key=api_key)

def encode_image_to_base64(image_path: str) -> str:
    """Convert image to base64 for OpenAI API"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_with_gpt4v(image_path: str) -> List[Dict]:
    """
    Use GPT-4V to extract ingredient data from receipt image
    
    Args:
        image_path: Path to the receipt image
        
    Returns:
        List of dictionaries with ingredient data
    """
    if not client:
        raise Exception("OpenAI client not initialized. Call init_openai_client() first.")
    
    try:
        # Encode image
        base64_image = encode_image_to_base64(image_path)
        
        # Create the prompt
        prompt = """
        Analyze this receipt image and extract all food/grocery items with their details.
        
        For each item, provide:
        - Ingredient name (cleaned up, no extra codes)
        - Quantity (with units like "2 kg", "1 pack", "500g", based on the item details you can be flexible)
        - Price (just the number with 2 decimal places)
        
        Return the data as a JSON array with this exact format:
        [
            {
                "Date": "2025-06-29",
                "Ingredient": "Whole Milk",
                "Quantity": "2 PT",
                "Price": "2.40",
                "Notes": ""
            }
        ]
        
        Rules:
        - Skip non-food items (bags, receipts, etc.)
        - Clean up ingredient names (remove barcodes, store codes)
        - Use the date on the receipt: 2025-06-29
        - Leave Notes field empty unless you deem necessary to add some info based on the receipt
        - Only return valid JSON, no explanations
        """
        
        # Make API call
        response = client.chat.completions.create(
            model="gpt-4o",  # or "gpt-4-vision-preview" if you have that
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000,
            temperature=0.1
        )
        
        # Parse response
        content = response.choices[0].message.content.strip()
        
        # Extract JSON from response (remove any markdown formatting)
        if content.startswith("```json"):
            content = content[7:-3]
        elif content.startswith("```"):
            content = content[3:-3]
        
        # Parse JSON
        items = json.loads(content)
        
        return items
        
    except json.JSONDecodeError as e:
        print(f"GPT-4V returned invalid JSON: {e}")
        return []
    except Exception as e:
        print(f"GPT-4V extraction error: {e}")
        return []

def check_api_access(api_key: str) -> Dict:
    """
    Check what models are available with the API key
    """
    try:
        temp_client = openai.OpenAI(api_key=api_key)
        models = temp_client.models.list()
        
        available_models = [model.id for model in models.data]
        vision_models = [m for m in available_models if 'gpt-4' in m and ('vision' in m or 'gpt-4o' in m)]
        
        return {
            "success": True,
            "total_models": len(available_models),
            "has_gpt4": any('gpt-4' in m for m in available_models),
            "vision_models": vision_models,
            "recommended": "gpt-4o" if "gpt-4o" in available_models else (
                "gpt-4-vision-preview" if "gpt-4-vision-preview" in available_models else None
            )
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
