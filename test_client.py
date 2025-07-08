#!/usr/bin/env python3
"""
MiniVault API Test Client

A comprehensive test client for testing the MiniVault API with various scenarios.
Run this script to automatically test all endpoints and functionality.
"""

import requests
import json
import time
import sys
from typing import Dict, Any, List

# API Configuration
API_BASE_URL = "http://localhost:8000"

class MiniVaultTestClient:
    """Test client for MiniVault API"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results: List[Dict[str, Any]] = []
    
    def test_health_check(self) -> bool:
        """Test the health check endpoint"""
        print("🏥 Testing health check endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed: {data['status']}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Could not connect to API. Make sure the server is running!")
            return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_generate_endpoint(self, prompt: str, expected_success: bool = True) -> bool:
        """Test the generate endpoint with a specific prompt"""
        print(f"🤖 Testing generate endpoint with prompt: '{prompt[:50]}{'...' if len(prompt) > 50 else ''}'")
        
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/generate",
                json={"prompt": prompt},
                headers={"Content-Type": "application/json"}
            )
            end_time = time.time()
            
            if expected_success:
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Response generated successfully in {int((end_time - start_time) * 1000)}ms")
                    print(f"   Model: {data.get('model', 'unknown')}")
                    print(f"   Response length: {len(data.get('response', ''))}")
                    print(f"   Response time (API): {data.get('response_time_ms', 'unknown')}ms")
                    return True
                else:
                    print(f"❌ Expected success but got {response.status_code}: {response.text}")
                    return False
            else:
                if response.status_code != 200:
                    print(f"✅ Expected failure and got {response.status_code}")
                    return True
                else:
                    print(f"❌ Expected failure but got success: {response.json()}")
                    return False
                    
        except Exception as e:
            print(f"❌ Generate endpoint error: {e}")
            return False
    
    def test_log_stats(self) -> bool:
        """Test the log stats endpoint"""
        print("📊 Testing log stats endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/logs/stats")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Log stats retrieved: {data.get('total_interactions', 0)} interactions")
                if data.get('total_interactions', 0) > 0:
                    print(f"   Average response time: {data.get('avg_response_time_ms', 0)}ms")
                    print(f"   Average prompt length: {data.get('avg_prompt_length', 0)} chars")
                return True
            else:
                print(f"❌ Log stats failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Log stats error: {e}")
            return False
    
    def run_comprehensive_tests(self):
        """Run a comprehensive test suite"""
        print("🚀 Starting MiniVault API Comprehensive Tests\n")
        
        # Test 1: Health check
        health_ok = self.test_health_check()
        if not health_ok:
            print("❌ Cannot proceed with tests - API is not responding")
            return False
        
        print()
        
        # Test 2: Valid prompts with different categories
        test_prompts = [
            # Code category
            "Write a Python function to sort a list",
            
            # Question category  
            "What is machine learning?",
            
            # Explanation category
            "Explain how neural networks work",
            
            # Creative category
            "Create a story about a robot",
            
            # Default category
            "This is a general statement about technology",
            
            # Long prompt
            "This is a very long prompt " * 20 + "that should test the system's ability to handle longer inputs effectively.",
            
            # Short prompt
            "Hi",
        ]
        
        success_count = 0
        for prompt in test_prompts:
            if self.test_generate_endpoint(prompt):
                success_count += 1
            print()
        
        # Test 3: Invalid prompts (should fail)
        print("🚫 Testing invalid prompts...")
        invalid_prompts = [
            "",  # Empty prompt
            "   ",  # Whitespace only
            "x" * 15000,  # Too long
        ]
        
        for prompt in invalid_prompts:
            if self.test_generate_endpoint(prompt, expected_success=False):
                success_count += 1
            print()
        
        # Test 4: Streaming response
        print("🌊 Testing streaming endpoint...")
        try:
            response = self.session.post(
                f"{self.base_url}/generate",
                json={"prompt": "Count to 5", "stream": True},
                stream=True,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                chunks_received = 0
                for line in response.iter_lines():
                    if line:
                        line_text = line.decode('utf-8')
                        if line_text.startswith('data: '):
                            chunks_received += 1
                            try:
                                chunk_data = json.loads(line_text[6:])
                                if chunk_data.get('is_final', False):
                                    break
                            except json.JSONDecodeError:
                                continue
                
                if chunks_received > 0:
                    print(f"✅ Streaming works: {chunks_received} chunks received")
                    success_count += 1
                else:
                    print("❌ No streaming chunks received")
            else:
                print(f"❌ Streaming failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Streaming error: {e}")
        
        print()

        # Test 5: Log stats
        if self.test_log_stats():
            success_count += 1
        
        print()
        
        # Test 5: Edge cases
        print("🔄 Testing edge cases...")
        edge_cases = [
            '{"special": "characters", "numbers": 123}',  # JSON-like input
            "Multiple\nlines\nof\ntext",  # Multi-line input
            "Special chars: !@#$%^&*()_+-=[]{}|;:,.<>?",  # Special characters
        ]
        
        for prompt in edge_cases:
            if self.test_generate_endpoint(prompt):
                success_count += 1
            print()
        
        total_tests = len(test_prompts) + len(invalid_prompts) + len(edge_cases) + 2  # +2 for health and stats
        
        print(f"🎯 Test Results: {success_count}/{total_tests} tests passed")
        
        if success_count == total_tests:
            print("🎉 All tests passed! API is working correctly.")
            return True
        else:
            print(f"⚠️  {total_tests - success_count} tests failed. Check the issues above.")
            return False

def interactive_mode():
    """Run the client in interactive mode"""
    client = MiniVaultTestClient()
    
    print("🤖 MiniVault API Interactive Test Client")
    print("Type your prompts to test the API. Type 'quit' to exit.\n")
    
    # Quick health check
    if not client.test_health_check():
        print("❌ API is not responding. Please start the server first.")
        return
    
    print()
    
    while True:
        try:
            prompt = input("Enter prompt: ").strip()
            
            if prompt.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not prompt:
                print("⚠️  Please enter a non-empty prompt")
                continue
            
            print()
            success = client.test_generate_endpoint(prompt)
            print()
            
            if not success:
                print("❌ Something went wrong with that request")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main function to run tests"""
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        client = MiniVaultTestClient()
        success = client.run_comprehensive_tests()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 