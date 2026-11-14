from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.shared.security import JWTManager

# auto_error=False: la validación real (y el 401) la decide quien consume el
# token (current_user o el proxy de forecasting); aquí solo se extrae.
_bearer_scheme = HTTPBearer(auto_error=False)


def bearer_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> str | None:
    """Dependencia de FastAPI: devuelve el token Bearer o None si no vino."""
    return credentials.credentials if credentials else None


def current_user(token: str | None = Depends(bearer_token)) -> str:
    """Dependencia de FastAPI: exige una sesión activa y devuelve el username.

    Se aplica a nivel de router en tracking, logistics, iot y products."""
    if not token:
        raise _unauthorized("Falta el token de acceso")
    try:
        payload = JWTManager().decode_active_token(token)
    except ValueError as exc:
        raise _unauthorized("Token inválido o expirado") from exc
    return payload["sub"]


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )
