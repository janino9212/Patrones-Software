import os
import threading
import logging

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

load_dotenv()

logger = logging.getLogger("scm.database")

# Default solo para desarrollo local sin .env configurado (Postgres local).
# En producción/nube, definir DATABASE_URL en el entorno o en .env (ver .env.example).
_DEFAULT_LOCAL_DATABASE_URL = (
    "postgresql://postgres:password123@localhost:5432/scm_db?client_encoding=utf8"
)

class DatabaseConnection:
    """Singleton que gestiona la única instancia del engine y sessionmaker."""

    _instance = None
    _lock = threading.Lock()  # thread-safety, importante porque FastAPI corre en varios workers/threads

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                # doble chequeo: evita condiciones de carrera si dos threads
                # entran casi al mismo tiempo antes de crear la instancia
                if cls._instance is None:
                    logger.info("Creando la única instancia de DatabaseConnection (Singleton)")
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
                else:
                    logger.info("Instancia ya existía, no se crea otra (Singleton en acción)")
        return cls._instance

    def _initialize(self):
        database_url = os.getenv("DATABASE_URL", _DEFAULT_LOCAL_DATABASE_URL)
        self._engine = create_engine(database_url)
        self._session_factory = sessionmaker(
            autocommit=False, autoflush=False, bind=self._engine
        )

    def get_session(self) -> Session:
        return self._session_factory()

    @property
    def engine(self):
        return self._engine


def get_db():
    """Dependencia de FastAPI: entrega una sesión por request, reutilizando el engine único."""
    db = DatabaseConnection().get_session()
    try:
        yield db
    finally:
        db.close()