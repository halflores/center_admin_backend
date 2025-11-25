import httpx
import sys

BASE_URL = "http://127.0.0.1:8000/api/v1/roles"

def test_create_role():
    print("Testing Create Role...")
    role_data = {
        "nombre": "Admin",
        "descripcion": "Administrator with full access"
    }
    try:
        response = httpx.post(BASE_URL + "/", json=role_data)
        if response.status_code == 200:
            print("✅ Role created successfully:", response.json())
            return response.json()['id']
        elif response.status_code == 400 and "already exists" in response.text:
             print("⚠️ Role already exists.")
             # Try to get the existing role to return its ID
             # For simplicity, let's just list roles and pick the first one if we can't create
             return 1 
        else:
            print("❌ Failed to create role:", response.text)
            return None
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None

def test_get_roles():
    print("\nTesting Get Roles...")
    try:
        response = httpx.get(BASE_URL + "/")
        if response.status_code == 200:
            print("✅ Retrieved roles:", response.json())
        else:
            print("❌ Failed to get roles:", response.text)
    except Exception as e:
        print(f"❌ Connection error: {e}")

def test_get_role(role_id):
    print(f"\nTesting Get Role {role_id}...")
    try:
        response = httpx.get(f"{BASE_URL}/{role_id}")
        if response.status_code == 200:
            print("✅ Retrieved role:", response.json())
        else:
            print("❌ Failed to get role:", response.text)
    except Exception as e:
        print(f"❌ Connection error: {e}")

def test_update_role(role_id):
    print(f"\nTesting Update Role {role_id}...")
    update_data = {
        "descripcion": "Updated description"
    }
    try:
        response = httpx.put(f"{BASE_URL}/{role_id}", json=update_data)
        if response.status_code == 200:
            print("✅ Role updated successfully:", response.json())
        else:
            print("❌ Failed to update role:", response.text)
    except Exception as e:
        print(f"❌ Connection error: {e}")

def test_delete_role(role_id):
    print(f"\nTesting Delete Role {role_id}...")
    try:
        response = httpx.delete(f"{BASE_URL}/{role_id}")
        if response.status_code == 200:
            print("✅ Role deleted successfully:", response.json())
        else:
            print("❌ Failed to delete role:", response.text)
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    role_id = test_create_role()
    if role_id:
        test_get_roles()
        test_get_role(role_id)
        test_update_role(role_id)
        # test_delete_role(role_id)
