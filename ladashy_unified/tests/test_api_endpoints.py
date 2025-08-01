#!/usr/bin/env python3
"""Simple API endpoint tester for LaDashy"""
import requests
import json
from test_config import TEST_SERVICES, API_BASE_URL

def test_endpoint(method, endpoint, data=None, description=""):
    """Test a single endpoint"""
    url = f"{API_BASE_URL}{endpoint}"
    print(f"\n{'='*60}")
    print(f"Testing: {description or endpoint}")
    print(f"Method: {method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ SUCCESS")
            if response.headers.get('content-type') == 'application/json':
                print(f"Response: {json.dumps(response.json(), indent=2)[:200]}...")
        else:
            print("❌ FAILED")
            print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ ERROR: {e}")

def run_all_tests():
    """Run all API tests"""
    print("🧪 LADASHY API TEST SUITE")
    
    # Test health endpoint
    test_endpoint("GET", "/api/health", description="Health Check")
    
    # Test service definitions
    test_endpoint("GET", "/api/services", description="Get Service Definitions")
    
    # Test Radarr connection
    if "radarr" in TEST_SERVICES:
        test_endpoint(
            "POST", 
            f"/api/services/radarr/{TEST_SERVICES['radarr']['host']}/test",
            TEST_SERVICES["radarr"],
            description="Test Radarr Connection"
        )
    
    # Test save configuration
    if "radarr" in TEST_SERVICES:
        test_endpoint(
            "POST",
            f"/api/services/radarr/{TEST_SERVICES['radarr']['host']}/config",
            TEST_SERVICES["radarr"],
            description="Save Radarr Configuration"
        )
    
    # Test dashboard generation
    test_endpoint("POST", "/api/generate", {}, description="Generate Dashboard")

if __name__ == "__main__":
    run_all_tests()
