#!/usr/bin/env python
import requests
import json

def test_registration():
    data = {
        'username': 'testuser123',
        'email': 'testuser123@example.com', 
        'password': 'testpassword123',
        'password2': 'testpassword123'
    }

    try:
        print("Testing registration endpoint...")
        response = requests.post('http://127.0.0.1:8000/api/auth/register/', json=data)
        print(f'Status Code: {response.status_code}')
        
        if response.status_code == 201:
            print("✅ Registration successful!")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print("❌ Registration failed!")
            try:
                error_data = response.json()
                print(f"Error response: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Raw response: {response.text}")
                
    except Exception as e:
        print(f'Error: {e}')

if __name__ == "__main__":
    test_registration()
