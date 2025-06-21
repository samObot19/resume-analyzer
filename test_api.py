#!/usr/bin/env python3
"""
Test script for Resume Analyzer API
"""

import requests
import json
import os
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
USERNAME = "admin"
PASSWORD = "admin123"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")

def test_login():
    """Test login endpoint"""
    print("\n🔐 Testing login endpoint...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": USERNAME, "password": PASSWORD}
        )
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Login successful")
            print(f"   Token type: {token_data['token_type']}")
            return token_data['access_token']
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_upload_without_token():
    """Test upload without authentication"""
    print("\n🚫 Testing upload without authentication...")
    try:
        # Create a dummy file for testing
        test_file = Path("test_resume.pdf")
        if not test_file.exists():
            test_file.write_bytes(b"%PDF-1.4\n%Test PDF content")
        
        response = requests.post(
            f"{BASE_URL}/upload",
            files={"file": ("test_resume.pdf", test_file.open("rb"), "application/pdf")}
        )
        if response.status_code == 401:
            print("✅ Upload correctly rejected without authentication")
        else:
            print(f"❌ Upload should have been rejected: {response.status_code}")
    except Exception as e:
        print(f"❌ Upload test error: {e}")

def test_upload_with_token(token):
    """Test upload with authentication"""
    print("\n📤 Testing upload with authentication...")
    try:
        # Create a dummy file for testing
        test_file = Path("test_resume.pdf")
        if not test_file.exists():
            test_file.write_bytes(b"%PDF-1.4\n%Test PDF content")
        
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{BASE_URL}/upload",
            headers=headers,
            files={"file": ("test_resume.pdf", test_file.open("rb"), "application/pdf")}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Upload successful")
            print(f"   Filename: {result['filename']}")
            print(f"   Webhook status: {result['webhook_status']['status']}")
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Upload test error: {e}")

def test_api_documentation():
    """Test API documentation endpoint"""
    print("\n📚 Testing API documentation...")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ API documentation available at /docs")
        else:
            print(f"❌ API documentation not available: {response.status_code}")
    except Exception as e:
        print(f"❌ Documentation test error: {e}")

def main():
    """Run all tests"""
    print("🧪 Resume Analyzer API Test Suite")
    print("=" * 50)
    
    # Test health
    test_health()
    
    # Test login
    token = test_login()
    
    # Test upload without token
    test_upload_without_token()
    
    # Test upload with token
    if token:
        test_upload_with_token(token)
    
    # Test API documentation
    test_api_documentation()
    
    print("\n" + "=" * 50)
    print("🏁 Test suite completed!")
    
    if token:
        print(f"\n💡 You can use this token for manual testing:")
        print(f"   Authorization: Bearer {token}")
        print(f"\n📖 API Documentation: {BASE_URL}/docs")
        print(f"🔧 n8n Interface: http://localhost:5678")
        print(f"🗄️  pgAdmin: http://localhost:5050")

if __name__ == "__main__":
    main() 