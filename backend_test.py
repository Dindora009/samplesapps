import requests
import unittest
import base64
import os
import json
from io import BytesIO
from PIL import Image
import numpy as np

# Get the backend URL from the frontend .env file
BACKEND_URL = "https://7611e9f5-93e7-4794-ad52-6cabf87fc260.preview.emergentagent.com"
API_URL = f"{BACKEND_URL}/api"

class VirtualTryOnAPITest(unittest.TestCase):
    
    def setUp(self):
        """Set up test data - create sample images for testing"""
        # Create a simple test image (red square)
        self.person_image = self._create_test_image((100, 200), (255, 0, 0))
        # Create another test image (blue square)
        self.clothing_image = self._create_test_image((100, 100), (0, 0, 255))
    
    def _create_test_image(self, size, color):
        """Helper to create a test image and convert to base64"""
        # Create a test image
        img = Image.new('RGB', size, color=color)
        
        # Save to BytesIO object
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        
        # Convert to base64
        img_byte_arr.seek(0)
        return base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
    
    def test_api_root(self):
        """Test the API root endpoint"""
        response = requests.get(f"{API_URL}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Hello World"})
        print("✅ API root endpoint test passed")
    
    def test_status_endpoint(self):
        """Test the status endpoint"""
        # Test POST
        post_data = {"client_name": "test_client"}
        post_response = requests.post(f"{API_URL}/status", json=post_data)
        self.assertEqual(post_response.status_code, 200)
        self.assertIn("id", post_response.json())
        self.assertEqual(post_response.json()["client_name"], "test_client")
        print("✅ POST status endpoint test passed")
        
        # Test GET
        get_response = requests.get(f"{API_URL}/status")
        self.assertEqual(get_response.status_code, 200)
        self.assertIsInstance(get_response.json(), list)
        print("✅ GET status endpoint test passed")
    
    def test_try_on_endpoint_without_api_key(self):
        """Test the try-on endpoint without an API key (should return an error)"""
        data = {
            "person_image": self.person_image,
            "clothing_image": self.clothing_image
        }
        
        response = requests.post(f"{API_URL}/try-on", json=data)
        
        # Since we don't have an OpenAI API key, we expect a 500 error
        self.assertEqual(response.status_code, 500)
        self.assertIn("detail", response.json())
        print("✅ Try-on endpoint correctly returns error when no API key is configured")
    
    def test_try_on_history_endpoint(self):
        """Test the try-on history endpoint"""
        response = requests.get(f"{API_URL}/try-on/history")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        print("✅ Try-on history endpoint test passed")

if __name__ == "__main__":
    print(f"Testing API at: {API_URL}")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
