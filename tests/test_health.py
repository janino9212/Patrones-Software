from fastapi.testclient import TestClient

from src.main import app
from src.shared.database import get_db


class _FakeSession:
    """Sesión de BD falsa que simula una consulta exitosa, sin tocar Postgres real."""

    def execute(self, *args, **kwargs):
        return None


class _FailingSession:
    """Sesión de BD falsa que simula una conexión caída."""

    def execute(self, *args, **kwargs):
        raise RuntimeError("sin conexión a la base de datos")


def _override_get_db(session):
    def _get_db():
        yield session

    return _get_db


def test_health_returns_ok_when_database_is_reachable():
    app.dependency_overrides[get_db] = _override_get_db(_FakeSession())
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected"}

    app.dependency_overrides.clear()


def test_health_returns_error_when_database_is_unreachable():
    app.dependency_overrides[get_db] = _override_get_db(_FailingSession())
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "error"
    assert body["database"] == "disconnected"

    app.dependency_overrides.clear()
