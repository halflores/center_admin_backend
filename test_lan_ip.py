import requests

def test_lan_ip():
    url = "http://192.168.0.17:8001/api/v1/audio-lessons/"
    print(f"Testing LAN URL: {url}")
    try:
        response = requests.get(url, timeout=2) # Short timeout
        print(f"Status Code: {response.status_code}")
        # We expect 401 Unauthorized, which means connection works
    except Exception as e:
        print(f"Error connecting to LAN IP: {e}")

if __name__ == "__main__":
    test_lan_ip()
