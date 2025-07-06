#!/usr/bin/env python3
"""
Test script for FastAPI server implementation.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mandatory .venv activation check
if "venv" not in sys.executable:
    raise RuntimeError("VENV NOT ACTIVATED. Please activate `.venv` before running this script.")

def test_fastapi_imports():
    """Test that FastAPI imports work correctly."""
    try:
        from fastapi import FastAPI, HTTPException, BackgroundTasks
        from fastapi.middleware.cors import CORSMiddleware
        from pydantic import BaseModel, Field
        print("✅ FastAPI imports successful")
        return True
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False

def test_pdfchat_imports():
    """Test that PDF Chat imports work correctly."""
    try:
        from pdfchat.config import Config
        from pdfchat.ingestion import PDFIngestion
        print("✅ PDF Chat imports successful")
        return True
    except ImportError as e:
        print(f"❌ PDF Chat import failed: {e}")
        return False

def test_fastapi_server_creation():
    """Test that FastAPI server can be created."""
    try:
        from pdfchat.fastapi_server import FastAPIQueryServer
        from pdfchat.config import Config
        
        # Create a test config
        config = Config()
        
        # Create the server
        server = FastAPIQueryServer(config)
        print("✅ FastAPI server creation successful")
        print(f"   - API Documentation: http://localhost:5000/docs")
        print(f"   - ReDoc Documentation: http://localhost:5000/redoc")
        print(f"   - OpenAPI Schema: http://localhost:5000/openapi.json")
        return True
    except Exception as e:
        print(f"❌ FastAPI server creation failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing FastAPI Server Implementation")
    print("=" * 50)
    
    tests = [
        ("FastAPI Imports", test_fastapi_imports),
        ("PDF Chat Imports", test_pdfchat_imports),
        ("FastAPI Server Creation", test_fastapi_server_creation),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! FastAPI server implementation is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Check dependencies and implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 