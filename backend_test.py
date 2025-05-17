import requests
import unittest
import json
import time
import sys

class AppCreationBotAPITest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get the backend URL from the frontend .env file
        self.base_url = "https://e3864b5b-11e2-4ebf-85a2-919b864a50ba.preview.emergentagent.com/api"
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}
        
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                if response.text:
                    try:
                        return success, response.json()
                    except json.JSONDecodeError:
                        return success, response.text
                return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"Response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_setup_api_keys(self):
        """Test setting up API keys"""
        print("\n===== Testing API Key Setup =====")
        # Test with valid OpenAI API key
        success, response = self.run_test(
            "Setup OpenAI API Key",
            "POST",
            "setup-api-keys",
            200,
            data={"openai": "sk-test-key-openai"}
        )
        self.assertTrue(success)
        
        # Test with valid Anthropic API key
        success, response = self.run_test(
            "Setup Anthropic API Key",
            "POST",
            "setup-api-keys",
            200,
            data={"anthropic": "sk-ant-test-key-anthropic"}
        )
        self.assertTrue(success)
        
        # Test with both API keys
        success, response = self.run_test(
            "Setup Both API Keys",
            "POST",
            "setup-api-keys",
            200,
            data={"openai": "sk-test-key-openai", "anthropic": "sk-ant-test-key-anthropic"}
        )
        self.assertTrue(success)

    def test_generate_app(self):
        """Test app generation endpoint"""
        print("\n===== Testing App Generation =====")
        # First set up API keys
        self.run_test(
            "Setup API Keys for Generation Test",
            "POST",
            "setup-api-keys",
            200,
            data={"openai": "sk-test-key-openai", "anthropic": "sk-ant-test-key-anthropic"}
        )
        
        # Test with valid app description and model
        success, response = self.run_test(
            "Generate App with Valid Description",
            "POST",
            "generate-app",
            200,
            data={"appDescription": "Create a simple todo app", "model": "gpt-3.5-turbo"}
        )
        
        if success and 'generationId' in response:
            generation_id = response['generationId']
            print(f"Generation ID: {generation_id}")
            
            # Test generation status endpoint
            print("\n===== Testing Generation Status =====")
            status_success, status_response = self.run_test(
                "Get Generation Status",
                "GET",
                f"generation-status/{generation_id}",
                200
            )
            
            self.assertTrue(status_success)
            if status_success:
                print(f"Generation Status: {status_response.get('status', 'unknown')}")
                
                # We won't wait for completion as it takes too long
                print("Note: Not waiting for generation to complete as it may take several minutes")
        else:
            print("Failed to get generation ID, skipping status check")

    def test_invalid_requests(self):
        """Test invalid requests to ensure proper error handling"""
        print("\n===== Testing Invalid Requests =====")
        
        # Test with empty app description
        success, response = self.run_test(
            "Generate App with Empty Description",
            "POST",
            "generate-app",
            400,  # Expecting bad request
            data={"appDescription": "", "model": "gpt-3.5-turbo"}
        )
        
        # Test with invalid model
        success, response = self.run_test(
            "Generate App with Invalid Model",
            "POST",
            "generate-app",
            400,  # Expecting bad request
            data={"appDescription": "Create a simple todo app", "model": "invalid-model"}
        )
        
        # Test with invalid generation ID
        success, response = self.run_test(
            "Get Status with Invalid Generation ID",
            "GET",
            "generation-status/invalid-id",
            404  # Expecting not found
        )

    def run_all_tests(self):
        """Run all tests and print summary"""
        try:
            self.test_setup_api_keys()
            self.test_generate_app()
            self.test_invalid_requests()
            
            print(f"\n📊 Tests completed: {self.tests_passed}/{self.tests_run} passed")
            return self.tests_passed == self.tests_run
        except Exception as e:
            print(f"Error running tests: {str(e)}")
            return False

if __name__ == "__main__":
    tester = AppCreationBotAPITest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)