import requests
import json

def test_api():
    base_url = "http://localhost:8001/api/v1"
    
    # 1. Login
    print("Attempting login...")
    login_data = {
        "username": "hal.flores@gmail.com",
        "password": "07.Hector"
    }
    try:
        login_response = requests.post(f"{base_url}/login/access-token", data=login_data)
        if login_response.status_code != 200:
            print(f"Login Failed: {login_response.status_code} - {login_response.text}")
            return
        
        token = login_response.json()["access_token"]
        print("Login Successful. Token obtained.")
        
        # 2. Get Lessons
        headers = {"Authorization": f"Bearer {token}"}
        lessons_url = f"{base_url}/audio-lessons/"
        print(f"Fetching lessons from: {lessons_url}")
        
        response = requests.get(lessons_url, headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Items count: {len(data.get('items', []))}")
            print(f"Total: {data.get('total')}")
            if len(data.get('items', [])) > 0:
                print("First item sample:", data['items'][0]['titulo'])
                print("Audio URL:", data['items'][0]['audio_url'])
        else:
            print("Response:", response.text)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
