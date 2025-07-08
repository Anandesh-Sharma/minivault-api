#!/usr/bin/env python3
"""
MiniVault API Advanced Test Client

Comprehensive test suite for the advanced MiniVault API including:
- Streaming responses
- Local LLM integration  
- Enhanced logging and performance metrics
- Advanced endpoints
"""

import requests
import json
import time
import sys
import asyncio
import aiohttp
from typing import Dict, Any, List
import os
from datetime import datetime

# API Configuration
API_BASE_URL = "http://localhost:8002"

class AdvancedMiniVaultTestClient:
    """Advanced test client for MiniVault API with streaming and LLM support"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results: List[Dict[str, Any]] = []
    
    def log_test_result(self, test_name: str, success: bool, details: str = "", response_time: float = 0):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "response_time_ms": round(response_time * 1000, 2),
            "timestamp": datetime.utcnow().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        time_str = f"({result['response_time_ms']}ms)" if response_time > 0 else ""
        print(f"{status} {test_name} {time_str}")
        if details:
            print(f"    {details}")
    
    def test_health_check_advanced(self) -> bool:
        """Test the enhanced health check endpoint"""
        print("🏥 Testing enhanced health check endpoint...")
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/health")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["status", "timestamp", "api_version", "model_type", "model_loaded", "system_info"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test_result("Health Check Advanced", False, f"Missing fields: {missing_fields}", response_time)
                    return False
                
                # Check system info structure
                system_info = data.get("system_info", {})
                expected_metrics = ["cpu_percent", "memory_percent", "memory_available_gb"]
                missing_metrics = [metric for metric in expected_metrics if metric not in system_info]
                
                if missing_metrics:
                    self.log_test_result("Health Check Advanced", False, f"Missing system metrics: {missing_metrics}", response_time)
                    return False
                
                self.log_test_result("Health Check Advanced", True, f"Status: {data['status']}, Model: {data['model_type']}", response_time)
                return True
            else:
                self.log_test_result("Health Check Advanced", False, f"HTTP {response.status_code}", response_time)
                return False
                
        except Exception as e:
            self.log_test_result("Health Check Advanced", False, f"Exception: {e}")
            return False
    
    def test_basic_generation_advanced(self) -> bool:
        """Test basic generation with enhanced features"""
        print("🎯 Testing enhanced generation endpoint...")
        try:
            start_time = time.time()
            response = self.session.post(
                f"{self.base_url}/generate",
                json={
                    "prompt": "Explain machine learning in simple terms",
                    "max_tokens": 50,
                    "temperature": 0.7
                }
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["response", "model", "response_time_ms"]
                optional_fields = ["tokens_generated", "model_info"]
                
                missing_required = [field for field in required_fields if field not in data]
                if missing_required:
                    self.log_test_result("Basic Generation Advanced", False, f"Missing required fields: {missing_required}", response_time)
                    return False
                
                # Check for enhanced fields
                has_tokens = "tokens_generated" in data
                has_model_info = "model_info" in data
                
                details = f"Generated {data.get('tokens_generated', 'unknown')} tokens"
                if has_model_info:
                    details += f", Model info available"
                
                self.log_test_result("Basic Generation Advanced", True, details, response_time)
                return True
            else:
                self.log_test_result("Basic Generation Advanced", False, f"HTTP {response.status_code}", response_time)
                return False
                
        except Exception as e:
            self.log_test_result("Basic Generation Advanced", False, f"Exception: {e}")
            return False
    
    async def test_streaming_response(self) -> bool:
        """Test streaming response functionality"""
        print("🌊 Testing streaming responses...")
        try:
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/generate",
                    json={
                        "prompt": "Tell me a short story about AI",
                        "max_tokens": 30,
                        "stream": True
                    }
                ) as response:
                    
                    if response.status != 200:
                        response_time = time.time() - start_time
                        self.log_test_result("Streaming Response", False, f"HTTP {response.status}", response_time)
                        return False
                    
                    chunks_received = 0
                    final_chunk_received = False
                    
                    async for line in response.content:
                        line_text = line.decode('utf-8').strip()
                        if line_text.startswith('data: '):
                            data_text = line_text[6:]  # Remove 'data: ' prefix
                            try:
                                chunk_data = json.loads(data_text)
                                chunks_received += 1
                                
                                if chunk_data.get('is_final', False):
                                    final_chunk_received = True
                                    break
                                    
                            except json.JSONDecodeError:
                                continue
                    
                    response_time = time.time() - start_time
                    
                    if chunks_received > 0 and final_chunk_received:
                        self.log_test_result("Streaming Response", True, f"Received {chunks_received} chunks", response_time)
                        return True
                    else:
                        self.log_test_result("Streaming Response", False, f"Only {chunks_received} chunks, final: {final_chunk_received}", response_time)
                        return False
                        
        except Exception as e:
            self.log_test_result("Streaming Response", False, f"Exception: {e}")
            return False
    
    def test_model_info_endpoint(self) -> bool:
        """Test model information endpoint"""
        print("🔍 Testing model info endpoint...")
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/models/info")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["model_type", "model_name", "status", "capabilities"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test_result("Model Info", False, f"Missing fields: {missing_fields}", response_time)
                    return False
                
                capabilities = data.get("capabilities", [])
                expected_capabilities = ["text_generation"]
                
                if not any(cap in capabilities for cap in expected_capabilities):
                    self.log_test_result("Model Info", False, f"Missing expected capabilities", response_time)
                    return False
                
                details = f"Model: {data['model_name']}, Type: {data['model_type']}, Capabilities: {len(capabilities)}"
                self.log_test_result("Model Info", True, details, response_time)
                return True
            else:
                self.log_test_result("Model Info", False, f"HTTP {response.status_code}", response_time)
                return False
                
        except Exception as e:
            self.log_test_result("Model Info", False, f"Exception: {e}")
            return False
    
    def test_enhanced_log_stats(self) -> bool:
        """Test enhanced log statistics"""
        print("📊 Testing enhanced log statistics...")
        try:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/logs/stats")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["total_requests", "avg_response_time_ms", "model_usage", "performance_metrics"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test_result("Enhanced Log Stats", False, f"Missing fields: {missing_fields}", response_time)
                    return False
                
                # Check performance metrics structure
                perf_metrics = data.get("performance_metrics", {})
                expected_metrics = ["min_response_time_ms", "max_response_time_ms"]
                
                has_advanced_metrics = any(metric in perf_metrics for metric in expected_metrics)
                
                details = f"Requests: {data['total_requests']}, Avg time: {data['avg_response_time_ms']}ms"
                if has_advanced_metrics:
                    details += ", Advanced metrics available"
                
                self.log_test_result("Enhanced Log Stats", True, details, response_time)
                return True
            else:
                self.log_test_result("Enhanced Log Stats", False, f"HTTP {response.status_code}", response_time)
                return False
                
        except Exception as e:
            self.log_test_result("Enhanced Log Stats", False, f"Exception: {e}")
            return False
    
    def test_parameter_validation_advanced(self) -> bool:
        """Test advanced parameter validation"""
        print("🔒 Testing advanced parameter validation...")
        
        test_cases = [
            {
                "name": "max_tokens too high",
                "payload": {"prompt": "Test", "max_tokens": 2000},
                "should_fail": True
            },
            {
                "name": "temperature too high", 
                "payload": {"prompt": "Test", "temperature": 3.0},
                "should_fail": True
            },
            {
                "name": "negative max_tokens",
                "payload": {"prompt": "Test", "max_tokens": -1},
                "should_fail": True
            },
            {
                "name": "valid parameters",
                "payload": {"prompt": "Test", "max_tokens": 50, "temperature": 0.8},
                "should_fail": False
            }
        ]
        
        passed = 0
        total = len(test_cases)
        
        for case in test_cases:
            try:
                start_time = time.time()
                response = self.session.post(f"{self.base_url}/generate", json=case["payload"])
                response_time = time.time() - start_time
                
                if case["should_fail"]:
                    success = response.status_code == 422  # Validation error
                else:
                    success = response.status_code == 200
                
                if success:
                    passed += 1
                    
            except Exception:
                if case["should_fail"]:
                    passed += 1
        
        success_rate = passed / total
        self.log_test_result("Advanced Parameter Validation", success_rate >= 0.75, f"{passed}/{total} tests passed")
        return success_rate >= 0.75
    
    def test_performance_under_load(self) -> bool:
        """Test API performance under load"""
        print("⚡ Testing performance under load...")
        
        num_requests = 10
        concurrent_requests = 3
        start_time = time.time()
        
        try:
            # Sequential requests
            sequential_times = []
            for i in range(num_requests):
                req_start = time.time()
                response = self.session.post(
                    f"{self.base_url}/generate",
                    json={"prompt": f"Test request {i}", "max_tokens": 20}
                )
                req_time = time.time() - req_start
                sequential_times.append(req_time)
                
                if response.status_code != 200:
                    self.log_test_result("Performance Under Load", False, f"Request {i} failed with {response.status_code}")
                    return False
            
            total_time = time.time() - start_time
            avg_response_time = sum(sequential_times) / len(sequential_times)
            requests_per_second = num_requests / total_time
            
            # Performance criteria
            success = (
                avg_response_time < 2.0 and  # Average response under 2 seconds
                requests_per_second > 2.0     # At least 2 RPS
            )
            
            details = f"Avg: {avg_response_time:.2f}s, RPS: {requests_per_second:.1f}"
            self.log_test_result("Performance Under Load", success, details, total_time)
            return success
            
        except Exception as e:
            self.log_test_result("Performance Under Load", False, f"Exception: {e}")
            return False
    
    async def run_async_tests(self):
        """Run tests that require async functionality"""
        print("\n🔄 Running async tests...")
        results = []
        
        # Streaming test
        results.append(await self.test_streaming_response())
        
        return results
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 Starting MiniVault API Advanced Test Suite")
        print("=" * 60)
        
        # Synchronous tests
        sync_tests = [
            self.test_health_check_advanced,
            self.test_basic_generation_advanced,
            self.test_model_info_endpoint,
            self.test_enhanced_log_stats,
            self.test_parameter_validation_advanced,
            self.test_performance_under_load
        ]
        
        sync_results = []
        for test in sync_tests:
            try:
                result = test()
                sync_results.append(result)
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
                sync_results.append(False)
        
        # Async tests
        try:
            async_results = asyncio.run(self.run_async_tests())
        except Exception as e:
            print(f"❌ Async tests failed: {e}")
            async_results = [False]
        
        # Combine results
        all_results = sync_results + async_results
        
        # Summary
        passed = sum(all_results)
        total = len(all_results)
        success_rate = (passed / total) * 100
        
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            print("🎉 Test suite PASSED!")
        else:
            print("⚠️ Test suite needs attention")
        
        return success_rate >= 80
    
    def run_interactive_demo(self):
        """Run interactive demo of advanced features"""
        print("\n🎮 Interactive Demo Mode")
        print("=" * 40)
        
        while True:
            print("\nAvailable commands:")
            print("1. Test basic generation")
            print("2. Test streaming generation") 
            print("3. Check model info")
            print("4. View log statistics")
            print("5. Exit")
            
            choice = input("\nEnter your choice (1-5): ").strip()
            
            if choice == "1":
                prompt = input("Enter your prompt: ").strip()
                if prompt:
                    try:
                        response = self.session.post(
                            f"{self.base_url}/generate",
                            json={"prompt": prompt, "max_tokens": 100}
                        )
                        if response.status_code == 200:
                            data = response.json()
                            print(f"\n✅ Response: {data['response']}")
                            print(f"📊 Tokens: {data.get('tokens_generated', 'N/A')}")
                            print(f"⏱️ Time: {data['response_time_ms']}ms")
                        else:
                            print(f"❌ Error: {response.status_code}")
                    except Exception as e:
                        print(f"❌ Exception: {e}")
            
            elif choice == "2":
                prompt = input("Enter your prompt for streaming: ").strip()
                if prompt:
                    print("\n🌊 Streaming response:")
                    try:
                        response = self.session.post(
                            f"{self.base_url}/generate",
                            json={"prompt": prompt, "max_tokens": 50, "stream": True},
                            stream=True
                        )
                        if response.status_code == 200:
                            for line in response.iter_lines():
                                if line:
                                    line_text = line.decode('utf-8')
                                    if line_text.startswith('data: '):
                                        try:
                                            chunk_data = json.loads(line_text[6:])
                                            if not chunk_data.get('is_final', False):
                                                print(chunk_data.get('token', ''), end='', flush=True)
                                            else:
                                                print(f"\n\n✅ Streaming complete!")
                                                break
                                        except json.JSONDecodeError:
                                            continue
                        else:
                            print(f"❌ Error: {response.status_code}")
                    except Exception as e:
                        print(f"❌ Exception: {e}")
            
            elif choice == "3":
                try:
                    response = self.session.get(f"{self.base_url}/models/info")
                    if response.status_code == 200:
                        data = response.json()
                        print(f"\n📋 Model Information:")
                        print(f"Type: {data.get('model_type')}")
                        print(f"Name: {data.get('model_name')}")
                        print(f"Status: {data.get('status')}")
                        print(f"Capabilities: {', '.join(data.get('capabilities', []))}")
                    else:
                        print(f"❌ Error: {response.status_code}")
                except Exception as e:
                    print(f"❌ Exception: {e}")
            
            elif choice == "4":
                try:
                    response = self.session.get(f"{self.base_url}/logs/stats")
                    if response.status_code == 200:
                        data = response.json()
                        print(f"\n📊 Log Statistics:")
                        print(f"Total requests: {data.get('total_requests')}")
                        print(f"Average response time: {data.get('avg_response_time_ms')}ms")
                        print(f"Last 24h requests: {data.get('last_24h_requests')}")
                        print(f"Model usage: {data.get('model_usage')}")
                    else:
                        print(f"❌ Error: {response.status_code}")
                except Exception as e:
                    print(f"❌ Exception: {e}")
            
            elif choice == "5":
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please try again.")

def main():
    """Main function"""
    client = AdvancedMiniVaultTestClient()
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        client.run_interactive_demo()
    else:
        client.run_all_tests()

if __name__ == "__main__":
    main() 