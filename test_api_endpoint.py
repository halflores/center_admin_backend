import requests
import json

def test_api():
    url = "http://localhost:8000/api/v1/audio-lessons/"
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Response JSON keys:", data.keys())
            print(f"Items count: {len(data.get('items', []))}")
            print(f"Total: {data.get('total')}")
            if len(data.get('items', [])) > 0:
                print("First item sample:", data['items'][0]['titulo'])
        else:
            print("Response:", response.text)
    except Exception as e:
        print(f"Error connecting to API: {e}")

if __name__ == "__main__":
    test_api()
