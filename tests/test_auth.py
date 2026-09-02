import pytest

from src.shared.security import JWTManager


@pytest.fixture(autouse=True)
def _clean_admin_session():
    """Evita que el token del usuario 'admin' se filtre entre tests,
    ya que JWTManager es un Singleton con estado compartido."""
    JWTManager().invalidate_token("admin")
    yield
    JWTManager().invalidate_token("admin")


def test_login_with_valid_credentials_returns_access_token(client_with_seeded_admin):
    response = client_with_seeded_admin.post(
        "/login", json={"username": "admin", "password": "admin123"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"


def test_login_with_invalid_password_returns_401(client_with_seeded_admin):
    response = client_with_seeded_admin.post(
        "/login", json={"username": "admin", "password": "clave-incorrecta"}
    )

    assert response.status_code == 401


def test_login_with_unknown_username_returns_401(client_with_seeded_admin):
    response = client_with_seeded_admin.post(
        "/login", json={"username": "usuario_que_no_existe", "password": "cualquiera"}
    )

    assert response.status_code == 401


def test_login_twice_without_logout_returns_409(client_with_seeded_admin):
    first_login = client_with_seeded_admin.post(
        "/login", json={"username": "admin", "password": "admin123"}
    )
    assert first_login.status_code == 200

    second_login = client_with_seeded_admin.post(
        "/login", json={"username": "admin", "password": "admin123"}
    )

    assert second_login.status_code == 409


def test_register_creates_new_user(client):
    response = client.post(
        "/register", json={"username": "nuevo_usuario", "password": "clave123"}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "nuevo_usuario"
    assert "password" not in body
    assert "hashed_password" not in body


def test_register_with_existing_username_returns_409(client_with_seeded_admin):
    response = client_with_seeded_admin.post(
        "/register", json={"username": "admin", "password": "otra-clave"}
    )

    assert response.status_code == 409


def test_register_then_login_with_new_user_works(client):
    register_response = client.post(
        "/register", json={"username": "otro_usuario", "password": "clave123"}
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/login", json={"username": "otro_usuario", "password": "clave123"}
    )

    assert login_response.status_code == 200
    JWTManager().invalidate_token("otro_usuario")
