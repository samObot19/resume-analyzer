#!/usr/bin/env python3
"""
Debug script for authentication testing
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_login():
    """Test login and get token"""
    print("🔐 Testing login...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"username": "admin", "password": "admin123"}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            token_data = response.json()
            return token_data['access_token']
        else:
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_auth_with_token(token):
    """Test authentication with token"""
    print(f"\n🔍 Testing auth with token: {token[:20]}...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/test-auth", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_upload_with_token(token):
    """Test upload with token"""
    print(f"\n📤 Testing upload with token: {token[:20]}...")
    try:
        # Create a dummy PDF file
        with open("test.pdf", "wb") as f:
            f.write(b"%PDF-1.4\n%Test PDF content")
        
        headers = {"Authorization": f"Bearer {token}"}
        with open("test.pdf", "rb") as f:
            files = {"file": ("test.pdf", f, "application/pdf")}
            response = requests.post(f"{BASE_URL}/upload", headers=headers, files=files)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("🧪 Authentication Debug Script")
    print("=" * 50)
    
    # Step 1: Get token
    token = test_login()
    if not token:
        print("❌ Failed to get token")
        return
    
    # Step 2: Test auth
    auth_ok = test_auth_with_token(token)
    if not auth_ok:
        print("❌ Authentication failed")
        return
    
    # Step 3: Test upload
    upload_ok = test_upload_with_token(token)
    if upload_ok:
        print("✅ All tests passed!")
    else:
        print("❌ Upload failed")

if __name__ == "__main__":
    main() 