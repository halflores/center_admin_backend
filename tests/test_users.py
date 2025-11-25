import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.session import get_db
from app.models.models import Base, Role, Usuario
from app.core.config import settings

# Use a separate test database or the same one (be careful)
# For simplicity, using the same one but we should clean up.
# Ideally use an in-memory SQLite for testing, but we are using Postgres specific features maybe?
# Let's stick to the configured DB but create unique data.

client = TestClient(app)

from app.core.security import get_password_hash

@pytest.fixture(scope="module")
def db():
    # Setup
    engine = create_engine(settings.DATABASE_URL)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    yield db
    # Teardown
    db.close()

@pytest.fixture(scope="module")
def admin_token(db):
    # Ensure role exists
    role = db.query(Role).filter(Role.nombre == "admin_test_role").first()
    if not role:
        role = Role(nombre="admin_test_role", descripcion="Role for admin testing")
        db.add(role)
        db.commit()
        db.refresh(role)
    
    # Ensure admin user exists
    email = "admin_test@example.com"
    password = "password123"
    user = db.query(Usuario).filter(Usuario.correo == email).first()
    if not user:
        user = Usuario(
            nombre="Admin",
            apellido="Test",
            correo=email,
            contrasena=get_password_hash(password),
            rol_id=role.id,
            activo=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
    # Login
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": email, "password": password}
    )
    return response.json()["access_token"]

def test_create_user(db, admin_token):
    # Ensure role exists
    role = db.query(Role).filter(Role.nombre == "test_role").first()
    if not role:
        role = Role(nombre="test_role", descripcion="Role for testing")
        db.add(role)
        db.commit()
        db.refresh(role)
    
    response = client.post(
        "/api/v1/users/",
        json={
            "nombre": "Test",
            "apellido": "User",
            "correo": "test@example.com",
            "contrasena": "password123",
            "rol_id": role.id,
            "activo": True
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    if response.status_code == 400 and "Email already registered" in response.text:
        # User already exists, try to get it to verify
        user = db.query(Usuario).filter(Usuario.correo == "test@example.com").first()
        assert user is not None
    else:
        assert response.status_code == 200
        data = response.json()
        assert data["correo"] == "test@example.com"
        assert "id" in data

def test_read_users(db, admin_token):
    # Authenticate first
    # We already have admin_token
    
    response = client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_update_user(db, admin_token):
    user = db.query(Usuario).filter(Usuario.correo == "test@example.com").first()
    assert user is not None
    
    response = client.put(
        f"/api/v1/users/{user.id}",
        json={"nombre": "Updated Name"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["nombre"] == "Updated Name"

def test_delete_user(db, admin_token):
    user = db.query(Usuario).filter(Usuario.correo == "test@example.com").first()
    assert user is not None
    
    response = client.delete(f"/api/v1/users/{user.id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    
    # Verify deletion
    response = client.get(f"/api/v1/users/{user.id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 404
