import urllib.request
import json

def check_api():
    url = "http://localhost:8001/api/v1/estudiantes/41"
    try:
        # We might need a token if it's protected. 
        # But let's try without first, or assume the user has a way to run it.
        # Actually, the endpoints seem to require `current_user`.
        # So this might return 401.
        
        # If it returns 401, I can't easily get a token without login.
        # But I can try to see if I can bypass or if I can use the debug_fetch approach 
        # but simulating the Pydantic serialization.
        
        print(f"Checking URL: {url}")
        req = urllib.request.Request(url)
        # Add a dummy token if needed, but I don't have one. 
        # Let's hope for the best or handle the error.
        
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            print("Response keys:", data.keys())
            if 'responsables' in data:
                print("responsables field is PRESENT")
                print("Value:", data['responsables'])
            else:
                print("responsables field is MISSING")
                
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} {e.reason}")
        if e.code == 401:
            print("Authentication required. Cannot verify API response directly without token.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_api()
