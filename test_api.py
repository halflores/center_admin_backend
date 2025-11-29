import requests
import json

# Login first
login_response = requests.post(
    "http://127.0.0.1:8001/api/v1/auth/login",
    data={
        "username": "hal.flores@gmail.com",
        "password": "07.hector"
    }
)

if login_response.status_code == 200:
    token = login_response.json()["access_token"]
    print("✅ Login successful")
    print(f"Token: {token[:50]}...")
    
    # Get permissions
    headers = {"Authorization": f"Bearer {token}"}
    perms_response = requests.get(
        "http://127.0.0.1:8001/api/v1/permisos/",
        headers=headers
    )
    
    if perms_response.status_code == 200:
        perms = perms_response.json()
        # Find a categorias_producto permission
        cat_perm = next((p for p in perms if p.get('funcion', {}).get('nombre') == 'categorias_producto'), None)
        if cat_perm:
            print("\n✅ Sample permission (categorias_producto):")
            print(json.dumps(cat_perm, indent=2, ensure_ascii=False))
        else:
            print("\n❌ No categorias_producto permission found")
            print(f"Total permissions: {len(perms)}")
            if perms:
                print("\nFirst permission:")
                print(json.dumps(perms[0], indent=2, ensure_ascii=False))
    else:
        print(f"❌ Failed to get permissions: {perms_response.status_code}")
        print(perms_response.text)
else:
    print(f"❌ Login failed: {login_response.status_code}")
    print(login_response.text)
