import logging
from contextlib import asynccontextmanager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

from fastapi import FastAPI
from src.shared.auth import router as auth_router
from src.shared.database import DatabaseConnection
from src.shared.health import router as health_router
from src.shared.models import Base
from src.shared.password_hashing import hash_password
from src.shared.user_repository import create_user, get_user_by_username
from src.tracking.interfaces.api import router as tracking_router

logger = logging.getLogger("scm.startup")

# Usuario de arranque para que Postman/pruebas manuales sigan funcionando
# igual que con el FAKE_USER anterior, ahora persistido en BD real.
_SEED_ADMIN_USERNAME = "admin"
_SEED_ADMIN_PASSWORD = "admin123"


def create_tables_and_seed_admin() -> None:
    engine = DatabaseConnection().engine
    Base.metadata.create_all(bind=engine)

    db = DatabaseConnection().get_session()
    try:
        if get_user_by_username(db, _SEED_ADMIN_USERNAME) is None:
            create_user(db, _SEED_ADMIN_USERNAME, hash_password(_SEED_ADMIN_PASSWORD))
            logger.info("Usuario 'admin' sembrado en la base de datos")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables_and_seed_admin()
    yield


app = FastAPI(title="SCM - Sistema de Gestión de Cadena de Suministro", lifespan=lifespan)

app.include_router(health_router, tags=["health"])
app.include_router(auth_router, tags=["auth"])
app.include_router(tracking_router)


@app.get("/")
def hola_mundo():
    return {"mensaje": "Hola mundo - SCM API"}
