import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.forecasting.application.forecast_commands import (
    ForecastCommandInvoker,
    get_command_invoker,
)
from src.iot.application.monitoring import SensorMonitor, get_sensor_monitor
from src.main import app
from src.shared.auth_dependencies import current_user
from src.shared.database import get_db
from src.shared.models import Base
from src.shared.password_hashing import hash_password
from src.shared.security import JWTManager
from src.shared.user_repository import create_user

_TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def db_session():
    """Sesión contra una BD SQLite en memoria, aislada por test.

    Se usa StaticPool para que todas las conexiones del engine reutilicen
    la misma conexión SQLite en memoria (si no, cada conexión nueva vería
    una BD vacía distinta). Así los tests no dependen de Neon/Postgres.
    """
    engine = create_engine(
        _TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = session_factory()

    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _client_for(db_session, authenticated: bool):
    def _override_get_db():
        yield db_session

    # Invoker y monitor nuevos por test: su estado vive en memoria del proceso.
    invoker = ForecastCommandInvoker()
    monitor = SensorMonitor()
    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_command_invoker] = lambda: invoker
    app.dependency_overrides[get_sensor_monitor] = lambda: monitor
    if authenticated:
        app.dependency_overrides[current_user] = lambda: "api_test_user"
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def client(db_session):
    """TestClient sobre la BD de prueba en memoria y con una sesión ya
    resuelta (current_user sobreescrito), para probar la lógica de los
    endpoints sin repetir el login en cada test."""
    yield from _client_for(db_session, authenticated=True)


@pytest.fixture
def anonymous_client(db_session):
    """Igual que `client` pero sin sesión: current_user valida el JWT real."""
    yield from _client_for(db_session, authenticated=False)


@pytest.fixture
def auth_headers():
    """Cabecera Authorization con un JWT válido para endpoints protegidos.

    JWTManager es un Singleton con estado compartido, así que se limpia la
    sesión del usuario de prueba antes y después de cada test."""
    username = "api_test_user"
    manager = JWTManager()
    manager.invalidate_token(username)
    token = manager.create_access_token(username)
    try:
        yield {"Authorization": f"Bearer {token}"}
    finally:
        manager.invalidate_token(username)


@pytest.fixture
def client_with_seeded_admin(anonymous_client, db_session):
    """Cliente con el usuario 'admin'/'admin123' ya creado en la BD de prueba."""
    create_user(db_session, "admin", hash_password("admin123"))
    return anonymous_client
