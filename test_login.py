#!/usr/bin/env python
import requests
import json

def test_login():
    data = {
        'username': 'testuser123',
        'password': 'testpassword123'
    }

    try:
        print("Testing login endpoint...")
        response = requests.post('http://127.0.0.1:8000/api/auth/login/', json=data)
        print(f'Status Code: {response.status_code}')
        
        if response.status_code == 200:
            print("✅ Login successful!")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print("❌ Login failed!")
            try:
                error_data = response.json()
                print(f"Error response: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Raw response: {response.text}")
                
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    test_login()
