import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

from fastapi import FastAPI
from src.shared.health import router as health_router
from src.shared.auth import router as auth_router

app = FastAPI(title="SCM - Sistema de Gestión de Cadena de Suministro")

app.include_router(health_router, tags=["health"])
app.include_router(auth_router, tags=["auth"])

@app.get("/")
def hola_mundo():
    return {"mensaje": "Hola mundo - SCM API"}