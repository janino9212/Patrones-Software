import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.shared.database import get_db
from src.shared.models import Base
from src.shared.password_hashing import hash_password
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


@pytest.fixture
def client(db_session):
    """TestClient con get_db sobreescrito para usar la BD de prueba en memoria."""

    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def client_with_seeded_admin(client, db_session):
    """Cliente con el usuario 'admin'/'admin123' ya creado en la BD de prueba."""
    create_user(db_session, "admin", hash_password("admin123"))
    return client
