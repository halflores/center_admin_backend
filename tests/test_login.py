import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.session import get_db
from app.models.models import Role, Usuario
from app.core.config import settings
from app.core.security import get_password_hash

client = TestClient(app)

@pytest.fixture(scope="module")
def db():
    engine = create_engine(settings.DATABASE_URL)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()

def test_login_access_token(db):
    # Ensure user exists
    email = "login_test@example.com"
    password = "password123"
    
    role = db.query(Role).filter(Role.nombre == "test_role").first()
    if not role:
        role = Role(nombre="test_role", descripcion="Role for testing")
        db.add(role)
        db.commit()
    
    user = db.query(Usuario).filter(Usuario.correo == email).first()
    if not user:
        hashed_password = get_password_hash(password)
        user = Usuario(
            nombre="Login",
            apellido="Test",
            correo=email,
            contrasena=hashed_password,
            rol_id=role.id,
            activo=True
        )
        db.add(user)
        db.commit()
    
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": email, "password": password}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_incorrect_password(db):
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": "login_test@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 400
