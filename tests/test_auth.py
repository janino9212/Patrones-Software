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


def _login(client) -> str:
    response = client.post("/login", json={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_second_login_replaces_the_previous_session(client_with_seeded_admin):
    first_token = _login(client_with_seeded_admin)
    second_token = _login(client_with_seeded_admin)

    assert second_token != first_token
    old = client_with_seeded_admin.get("/me", headers={"Authorization": f"Bearer {first_token}"})
    new = client_with_seeded_admin.get("/me", headers={"Authorization": f"Bearer {second_token}"})
    assert old.status_code == 401
    assert new.status_code == 200
    assert new.json()["message"] == "admin"


def test_logout_invalidates_the_token(client_with_seeded_admin):
    headers = {"Authorization": f"Bearer {_login(client_with_seeded_admin)}"}

    logout = client_with_seeded_admin.post("/logout", headers=headers)

    assert logout.status_code == 200
    assert client_with_seeded_admin.get("/me", headers=headers).status_code == 401


def test_logout_without_token_returns_401(client_with_seeded_admin):
    response = client_with_seeded_admin.post("/logout")

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_register_rejects_username_with_invalid_characters(client):
    response = client.post("/register", json={"username": "a b<script>", "password": "clave123"})

    assert response.status_code == 422


@pytest.mark.parametrize(
    "method, path",
    [
        ("get", "/tracking/events/PROD-1"),
        ("get", "/logistics/routes"),
        ("get", "/iot/alerts"),
        ("get", "/products"),
        ("get", "/forecasting/plans/PROD-1"),
    ],
)
def test_business_endpoints_require_a_session(anonymous_client, method, path):
    response = getattr(anonymous_client, method)(path)

    assert response.status_code == 401


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
