#!/usr/bin/env python3
"""
Simple test script to verify API imports and basic functionality
"""
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from api.main import app
    print("✅ API imports successfully")
    
    # Test basic app functionality
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    # Test root endpoint
    response = client.get("/")
    if response.status_code == 200:
        print("✅ API root endpoint works")
    else:
        print(f"❌ API root endpoint failed: {response.status_code}")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")

print("API test completed")
