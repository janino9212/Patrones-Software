import logging
import os
from contextlib import asynccontextmanager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

from fastapi import Depends, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.logistics.interfaces.api import router as logistics_router
from src.shared.auth import router as auth_router
from src.shared.auth_dependencies import current_user
from src.shared.database import DatabaseConnection
from src.shared.health import router as health_router
from src.shared.models import Base
from src.shared.password_hashing import hash_password
from src.shared.schema_migrations import apply_added_columns
from src.shared.user_repository import create_user, get_user_by_username
from src.tracking.interfaces.api import router as tracking_router
from src.forecasting.interfaces.api import router as forecasting_router
from src.iot.interfaces.api import router as iot_router
from src.products.interfaces.api import router as products_router

logger = logging.getLogger("scm.startup")

# Usuario de arranque para que Postman/pruebas manuales sigan funcionando
# igual que con el FAKE_USER anterior, ahora persistido en BD real.
_SEED_ADMIN_USERNAME = "admin"
_SEED_ADMIN_PASSWORD = "admin123"


def create_tables_and_seed_admin() -> None:
    engine = DatabaseConnection().engine
    Base.metadata.create_all(bind=engine)
    apply_added_columns(engine)

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

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Responde 422 sin devolver el valor recibido.

    El manejador por defecto incluye `input` en cada error: eso repite en la
    respuesta lo que envió el cliente (contraseñas incluidas) y falla con 500
    cuando el valor no es JSON válido, como `Infinity`."""
    detail = [
        {"type": error.get("type"), "loc": list(error.get("loc", ())), "msg": error.get("msg")}
        for error in exc.errors()
    ]
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": detail})


# Orígenes del frontend autorizados a llamar la API desde el navegador.
_DEFAULT_CORS_ORIGINS = "http://localhost:5173,http://127.0.0.1:5173"
_cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", _DEFAULT_CORS_ORIGINS).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Los routers de negocio exigen sesión activa. forecasting (reportes) y
# products (overview) además pasan por el Proxy de protección.
_session_required = [Depends(current_user)]

app.include_router(health_router, tags=["health"])
app.include_router(auth_router, tags=["auth"])
app.include_router(tracking_router, dependencies=_session_required)
app.include_router(logistics_router, dependencies=_session_required)
app.include_router(iot_router, dependencies=_session_required)
app.include_router(forecasting_router)
app.include_router(products_router)


@app.get("/")
def api_root():
    return {"mensaje": "SCM API", "docs": "/docs"}
