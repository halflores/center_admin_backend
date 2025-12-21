import httpx
import sys

BASE_URL = "http://127.0.0.1:8001/api/v1/roles"

def get_roles():
    try:
        response = httpx.get(BASE_URL + "/")
        if response.status_code == 200:
            roles = response.json()
            print("Existing Roles:")
            for role in roles:
                print(f"ID: {role['id']}, Name: {role['nombre']}")
        else:
            print("Failed to get roles:", response.status_code, response.text)
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    get_roles()
