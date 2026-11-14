import logging

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.shared.database import get_db

logger = logging.getLogger("scm.health")

router = APIRouter()


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception:  # cualquier fallo significa "sin base de datos"
        # El detalle (host, usuario, base) queda en el log del servidor; este
        # endpoint es público y no debe exponerlo.
        logger.exception("La comprobación de la base de datos falló")
        return {"status": "error", "database": "disconnected"}
    return {"status": "ok", "database": "connected"}
