import unittest
from app.agent.parser import parse_receipt_lines, extract_item_from_line, clean_item_name

class TestParser(unittest.TestCase):
    
    def test_extract_item_from_line(self):
        """Test extracting item data from receipt lines"""
        
        # Test basic item with price
        line = "Whole Milk 2.40"
        result = extract_item_from_line(line, "2025-06-29")
        
        self.assertIsNotNone(result)
        self.assertEqual(result['Ingredient'], "Whole Milk")
        self.assertEqual(result['Price'], "2.40")
        self.assertEqual(result['Date'], "2025-06-29")
    
    def test_extract_with_quantity(self):
        """Test extracting items with quantities"""
        
        line = "2 x Bread 3.20"
        result = extract_item_from_line(line, "2025-06-29")
        
        self.assertIsNotNone(result)
        self.assertEqual(result['Quantity'], "2 x")
        self.assertEqual(result['Price'], "3.20")
    
    def test_clean_item_name(self):
        """Test item name cleaning"""
        
        # Test removing quantity
        result = clean_item_name("2 x Organic Milk", "2 x")
        self.assertEqual(result, "Milk")
        
        # Test title case
        result = clean_item_name("whole milk", "")
        self.assertEqual(result, "Whole Milk")
    
    def test_parse_full_receipt(self):
        """Test parsing multiple lines"""
        
        lines = [
            "GROCERY STORE",
            "Whole Milk 2.40",
            "Bread 2x 3.20", 
            "Total: 5.60",
            "Thank you"
        ]
        
        result = parse_receipt_lines(lines)
        
        # Should extract 2 items (skip header/footer)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['Ingredient'], "Whole Milk")
        self.assertEqual(result[1]['Price'], "3.20")

if __name__ == '__main__':
    unittest.main()
