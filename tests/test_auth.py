import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.shared.security import JWTManager

client = TestClient(app)


@pytest.fixture(autouse=True)
def _clean_admin_session():
    """Evita que el token del usuario 'admin' se filtre entre tests,
    ya que JWTManager es un Singleton con estado compartido."""
    JWTManager().invalidate_token("admin")
    yield
    JWTManager().invalidate_token("admin")


def test_login_with_valid_credentials_returns_access_token():
    response = client.post("/login", json={"username": "admin", "password": "admin123"})

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"


def test_login_with_invalid_credentials_returns_401():
    response = client.post("/login", json={"username": "admin", "password": "clave-incorrecta"})

    assert response.status_code == 401


def test_login_twice_without_logout_returns_409():
    first_login = client.post("/login", json={"username": "admin", "password": "admin123"})
    assert first_login.status_code == 200

    second_login = client.post("/login", json={"username": "admin", "password": "admin123"})

    assert second_login.status_code == 409
