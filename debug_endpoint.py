import requests
import sys

# Try both localhost and IP
urls = [
    "http://localhost:8001/api/v1/audio-lessons/3/stream",
    "http://192.168.0.17:8001/api/v1/audio-lessons/3/stream"
]

def test_url(url):
    print(f"Testing {url}...")
    try:
        # Just head or get with stream=True
        response = requests.get(url, stream=True)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Error Content: {response.text}")
            print(f"Headers: {response.headers}")
        else:
            print("Success! Stream works.")
            # Consume a bit
            chunk = next(response.iter_content(chunk_size=1024))
            print(f"First 1KB bytes received. Length: {len(chunk)}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    for url in urls:
        test_url(url)
        print("-" * 20)
