import requests
import sys
import time
import uuid
from datetime import datetime

class AppCreationBotTester:
    def __init__(self, base_url="https://e3864b5b-11e2-4ebf-85a2-919b864a50ba.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def run_test(self, name, method, endpoint, expected_status, data=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
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
                try:
                    response_data = response.json()
                    print(f"Response: {response_data}")
                    self.test_results.append({
                        "name": name,
                        "success": True,
                        "status_code": response.status_code,
                        "response": response_data
                    })
                    return success, response_data
                except:
                    print(f"Response: {response.text}")
                    self.test_results.append({
                        "name": name,
                        "success": True,
                        "status_code": response.status_code,
                        "response": response.text
                    })
                    return success, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"Response: {response_data}")
                    self.test_results.append({
                        "name": name,
                        "success": False,
                        "status_code": response.status_code,
                        "response": response_data
                    })
                except:
                    print(f"Response: {response.text}")
                    self.test_results.append({
                        "name": name,
                        "success": False,
                        "status_code": response.status_code,
                        "response": response.text
                    })
                return success, None

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.test_results.append({
                "name": name,
                "success": False,
                "error": str(e)
            })
            return False, None

    def test_api_status(self):
        """Test the API status endpoint"""
        return self.run_test(
            "API Status Check",
            "GET",
            "",
            200
        )

    def test_setup_openai_api_key(self):
        """Test setting up the OpenAI API key"""
        return self.run_test(
            "Setup OpenAI API Key",
            "POST",
            "setup-api-keys",
            200,
            data={"openai": "sk-test-key-openai"}
        )

    def test_setup_anthropic_api_key(self):
        """Test setting up the Anthropic API key"""
        return self.run_test(
            "Setup Anthropic API Key",
            "POST",
            "setup-api-keys",
            200,
            data={"anthropic": "sk-ant-test-key-anthropic"}
        )

    def test_setup_both_api_keys(self):
        """Test setting up both API keys"""
        return self.run_test(
            "Setup Both API Keys",
            "POST",
            "setup-api-keys",
            200,
            data={"openai": "sk-test-key-openai", "anthropic": "sk-ant-test-key-anthropic"}
        )

    def test_generate_app(self, model="gpt-3.5-turbo"):
        """Test generating an app"""
        success, response = self.run_test(
            "Generate App with Valid Description",
            "POST",
            "generate-app",
            200,
            data={
                "appDescription": "Create a simple todo app with user authentication",
                "model": model
            }
        )
        
        if success and response and "generation_id" in response:
            generation_id = response["generation_id"]
            print(f"Generation ID: {generation_id}")
            return generation_id
        return None

    def test_generation_status(self, generation_id):
        """Test getting the generation status"""
        return self.run_test(
            "Get Generation Status",
            "GET",
            f"generation-status/{generation_id}",
            200
        )

    def run_all_tests(self):
        """Run all tests"""
        print("===== Testing API Key Setup =====\n")
        
        # Test API status
        self.test_api_status()
        
        # Test API key setup
        self.test_setup_openai_api_key()
        self.test_setup_anthropic_api_key()
        self.test_setup_both_api_keys()
        
        print("\n===== Testing App Generation =====\n")
        
        # Setup API keys for generation test
        success, _ = self.test_setup_both_api_keys()
        if not success:
            print("❌ Failed to setup API keys for generation test")
            return False
        
        # Test app generation
        generation_id = self.test_generate_app()
        if not generation_id:
            print("❌ Failed to generate app")
            return False
        
        print("\n===== Testing Generation Status =====\n")
        
        # Test generation status
        success, _ = self.test_generation_status(generation_id)
        if not success:
            print("❌ Failed to get generation status")
            return False
        
        # Print test results
        print(f"\n📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = AppCreationBotTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
