import easyocr
from PIL import Image
import numpy as np

def extract_text_from_image(image_path: str) -> list:
    """
    Extract text lines from receipt image using EasyOCR
    
    Args:
        image_path: Path to the receipt image
        
    Returns:
        List of text lines detected in the image
    """
    try:
        # Initialize EasyOCR reader
        reader = easyocr.Reader(['en'])
        
        # Read image and extract text
        results = reader.readtext(image_path)
        
        # Extract just the text strings, sorted by vertical position
        text_lines = []
        for (bbox, text, confidence) in results:
            if confidence > 0.5:  # Filter out low-confidence detections
                text_lines.append({
                    'text': text.strip(),
                    'confidence': confidence,
                    'bbox': bbox
                })
        
        # Sort by y-coordinate (top to bottom)
        text_lines.sort(key=lambda x: x['bbox'][0][1])
        
        # Return just the text strings
        return [line['text'] for line in text_lines]
        
    except Exception as e:
        print(f"OCR Error: {e}")
        return []

def preprocess_image(image_path: str) -> str:
    """
    Optional: Preprocess image for better OCR results
    """
    try:
        img = Image.open(image_path)
        
        # Convert to grayscale
        img = img.convert('L')
        
        # Enhance contrast if needed
        # You can add more preprocessing here
        
        processed_path = f"processed_{image_path}"
        img.save(processed_path)
        return processed_path
        
    except Exception as e:
        print(f"Preprocessing error: {e}")
        return image_path
