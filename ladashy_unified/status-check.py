#!/usr/bin/env python3
"""
LaDashy Project Status Checker
Verifies what's actually working vs what documentation says
"""
import os
import json
import subprocess
import requests
from datetime import datetime

class ProjectStatusChecker:
    def __init__(self):
        self.project_root = "/home/zach/homelab-documentation/ladashy_unified"
        self.api_url = "http://localhost:5000/api"
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "backend": {},
            "frontend": {},
            "features": {},
            "documentation": {}
        }
    
    def check_backend_running(self):
        """Check if backend API is running"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=2)
            self.results["backend"]["running"] = True
            self.results["backend"]["health"] = response.json()
            return True
        except:
            self.results["backend"]["running"] = False
            return False
    
    def check_api_endpoints(self):
        """Test each API endpoint"""
        endpoints = [
            ("GET", "/health", None),
            ("GET", "/services", None),
            ("GET", "/scan/status", None),
        ]
        
        self.results["backend"]["endpoints"] = {}
        
        for method, endpoint, data in endpoints:
            try:
                url = f"{self.api_url}{endpoint}"
                if method == "GET":
                    response = requests.get(url, timeout=2)
                else:
                    response = requests.post(url, json=data, timeout=2)
                
                self.results["backend"]["endpoints"][endpoint] = {
                    "status": response.status_code,
                    "working": response.status_code < 400
                }
            except Exception as e:
                self.results["backend"]["endpoints"][endpoint] = {
                    "status": "error",
                    "working": False,
                    "error": str(e)
                }
    
    def check_frontend_files(self):
        """Check frontend file integrity"""
        frontend_path = os.path.join(self.project_root, "frontend")
        
        # Check for syntax errors in index.html
        index_path = os.path.join(frontend_path, "index.html")
        if os.path.exists(index_path):
            with open(index_path, 'r') as f:
                content = f.read()
            
            # Quick syntax checks
            self.results["frontend"]["index_exists"] = True
            self.results["frontend"]["duplicate_const"] = content.count("const apiKey") > 1
            self.results["frontend"]["script_tags_balanced"] = content.count("<script>") == content.count("</script>")
            
            # Check for key functions
            key_functions = [
                "discoverServices",
                "addManualService", 
                "saveServiceConfig",
                "testServiceConnection",
                "generateDashboard"
            ]
            
            self.results["frontend"]["functions"] = {}
            for func in key_functions:
                self.results["frontend"]["functions"][func] = f"function {func}" in content
    
    def check_documentation_consistency(self):
        """Check if documentation matches reality"""
        docs_path = os.path.join(self.project_root, "docs/project_knowledge")
        
        # Check Progress Tracker
        progress_path = os.path.join(docs_path, "PROGRESS_TRACKER.md")
        if os.path.exists(progress_path):
            with open(progress_path, 'r') as f:
                progress_content = f.read()
            self.results["documentation"]["progress_tracker_exists"] = True
            self.results["documentation"]["section_01_status"] = "❌ Not Started" in progress_content
        
        # Check Section 01 Complete
        section01_path = os.path.join(docs_path, "SECTION_01_COMPLETE.md")
        self.results["documentation"]["section_01_complete_exists"] = os.path.exists(section01_path)
        
        # Documentation conflict!
        if self.results["documentation"].get("section_01_complete_exists") and self.results["documentation"].get("section_01_status"):
            self.results["documentation"]["conflict"] = "Section 01 marked complete in file but not started in Progress Tracker"
    
    def check_feature_status(self):
        """Check which features are actually working"""
        features = {
            "network_scanning": False,
            "manual_service_add": False,
            "service_configuration": False,
            "service_testing": False,
            "dashboard_generation": False
        }
        
        # Can only check these if backend is running
        if self.results["backend"].get("running"):
            # Check if we have any services discovered
            try:
                response = requests.get(f"{self.api_url}/services")
                if response.status_code == 200:
                    services = response.json()
                    features["network_scanning"] = len(services) > 0
            except:
                pass
        
        self.results["features"] = features
    
    def generate_report(self):
        """Generate status report"""
        print("=" * 60)
        print("🔍 LaDashy Project Status Report")
        print("=" * 60)
        print(f"Generated: {self.results['timestamp']}")
        print()
        
        # Backend Status
        print("🔧 BACKEND STATUS:")
        if self.results["backend"].get("running"):
            print("  ✅ API Server: RUNNING")
            for endpoint, status in self.results["backend"].get("endpoints", {}).items():
                symbol = "✅" if status["working"] else "❌"
                print(f"  {symbol} {endpoint}: {status['status']}")
        else:
            print("  ❌ API Server: NOT RUNNING")
            print("     Run: python backend/api.py")
        print()
        
        # Frontend Status
        print("🖥️  FRONTEND STATUS:")
        if self.results["frontend"].get("index_exists"):
            print("  ✅ index.html exists")
            if self.results["frontend"].get("duplicate_const"):
                print("  ❌ Duplicate const declarations found!")
            else:
                print("  ✅ No duplicate const declarations")
            
            print("\n  Function Status:")
            for func, exists in self.results["frontend"].get("functions", {}).items():
                symbol = "✅" if exists else "❌"
                print(f"  {symbol} {func}()")
        print()
        
        # Documentation Status
        print("📚 DOCUMENTATION STATUS:")
        if self.results["documentation"].get("conflict"):
            print(f"  ⚠️  CONFLICT: {self.results['documentation']['conflict']}")
        print()
        
        # Feature Status
        print("🚀 FEATURE STATUS:")
        for feature, working in self.results["features"].items():
            symbol = "✅" if working else "❌"
            print(f"  {symbol} {feature.replace('_', ' ').title()}")
        print()
        
        # Summary
        print("=" * 60)
        print("📊 SUMMARY:")
        
        # Count working vs broken
        backend_working = sum(1 for e in self.results["backend"].get("endpoints", {}).values() if e["working"])
        backend_total = len(self.results["backend"].get("endpoints", {}))
        
        frontend_working = sum(1 for f in self.results["frontend"].get("functions", {}).values() if f)
        frontend_total = len(self.results["frontend"].get("functions", {}))
        
        feature_working = sum(1 for f in self.results["features"].values() if f)
        feature_total = len(self.results["features"])
        
        print(f"  Backend Endpoints: {backend_working}/{backend_total} working")
        print(f"  Frontend Functions: {frontend_working}/{frontend_total} exist")
        print(f"  Features: {feature_working}/{feature_total} working")
        
        # Save detailed results
        output_path = os.path.join(self.project_root, "project_status.json")
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Detailed results saved to: project_status.json")
        print("=" * 60)

if __name__ == "__main__":
    checker = ProjectStatusChecker()
    checker.check_backend_running()
    checker.check_api_endpoints()
    checker.check_frontend_files()
    checker.check_documentation_consistency()
    checker.check_feature_status()
    checker.generate_report()