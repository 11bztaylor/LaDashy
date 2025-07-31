#!/usr/bin/env python3
"""Quick API test"""
import requests
import time

print("Testing LaDashy API...")

# Wait for server to start
time.sleep(2)

try:
    # Test health endpoint
    response = requests.get('http://localhost:5000/api/health')
    if response.status_code == 200:
        print("✅ API is healthy:", response.json())
    else:
        print("❌ API returned:", response.status_code)
except Exception as e:
    print("❌ Could not connect to API:", e)
    print("Make sure to run ./run_ladashy.sh first!")
