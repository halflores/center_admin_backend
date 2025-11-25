import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.session import get_db
from app.models.models import Base, Role, Usuario
from app.core.config import settings
from app.core.security import get_password_hash

# Setup Test DB
engine = create_engine(settings.DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def db():
    db = TestingSessionLocal()
    yield db
    db.close()

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def test_user_token(db, client):
    # Ensure role exists
    role = db.query(Role).filter(Role.nombre == "auth_test_role").first()
    if not role:
        role = Role(nombre="auth_test_role", descripcion="Role for auth testing")
        db.add(role)
        db.commit()
        db.refresh(role)
    
    # Ensure user exists
    email = "auth_test@example.com"
    password = "password123"
    user = db.query(Usuario).filter(Usuario.correo == email).first()
    if not user:
        user = Usuario(
            nombre="Auth",
            apellido="Test",
            correo=email,
            contrasena=get_password_hash(password),
            rol_id=role.id,
            activo=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Login to get token
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": email, "password": password}
    )
    assert response.status_code == 200
    return response.json()["access_token"]

def test_roles_protected(client, test_user_token):
    # Try without token
    response = client.get("/api/v1/roles/")
    assert response.status_code == 401
    
    # Try with token
    response = client.get(
        "/api/v1/roles/",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_users_protected(client, test_user_token):
    # Try without token
    response = client.get("/api/v1/users/")
    assert response.status_code == 401
    
    # Try with token
    response = client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_create_role_protected(client, test_user_token):
    # Try without token
    response = client.post("/api/v1/roles/", json={"nombre": "NewRole", "descripcion": "Desc"})
    assert response.status_code == 401
    
    # Try with token
    # Note: We might fail if role exists, but status should not be 401
    response = client.post(
        "/api/v1/roles/",
        json={"nombre": "NewRoleAuth", "descripcion": "Desc"},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code in [200, 400] # 400 if exists

def test_create_user_protected(client, test_user_token, db):
    # Get a role id
    role = db.query(Role).first()
    
    user_data = {
        "nombre": "New",
        "apellido": "User",
        "correo": "newuserauth@example.com",
        "contrasena": "password123",
        "rol_id": role.id,
        "activo": True
    }
    
    # Try without token
    response = client.post("/api/v1/users/", json=user_data)
    assert response.status_code == 401
    
    # Try with token
    response = client.post(
        "/api/v1/users/",
        json=user_data,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code in [200, 400]
