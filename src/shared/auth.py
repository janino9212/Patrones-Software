import os

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.shared.auth_dependencies import bearer_token, current_user
from src.shared.auth_schemas import (
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from src.shared.database import get_db
from src.shared.password_hashing import hash_password, verify_password
from src.shared.security import JWTManager
from src.shared.user_repository import create_user, get_user_by_username

router = APIRouter()

# Hash de relleno: cuando el usuario no existe se verifica contra él, para que
# la respuesta tarde lo mismo y no revele qué usuarios existen.
_PLACEHOLDER_HASH = hash_password("relleno-para-igualar-el-tiempo-de-respuesta")


def _is_registration_allowed() -> bool:
    return os.getenv("ALLOW_REGISTRATION", "true").strip().lower() in ("1", "true", "yes")


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_username(db, credentials.username)
    stored_hash = user.hashed_password if user is not None else _PLACEHOLDER_HASH
    password_matches = verify_password(credentials.password, stored_hash)
    if user is None or not password_matches:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

    # Un login correcto reemplaza la sesión anterior del usuario (si la había).
    token = JWTManager().create_access_token(username=credentials.username)
    return TokenResponse(access_token=token, username=credentials.username)


@router.post("/logout", response_model=MessageResponse)
def logout(
    username: str = Depends(current_user),
    token: str | None = Depends(bearer_token),
):
    JWTManager().invalidate_token(username, token)
    return MessageResponse(message="Sesión cerrada")


@router.get("/me", response_model=MessageResponse)
def me(username: str = Depends(current_user)):
    """Permite al frontend comprobar si el token guardado sigue activo."""
    return MessageResponse(message=username)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if not _is_registration_allowed():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El registro de usuarios está deshabilitado",
        )
    if get_user_by_username(db, payload.username) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El usuario ya existe")

    user = create_user(db, payload.username, hash_password(payload.password))
    return user
