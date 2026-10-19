from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# auto_error=False: la validación real (y el 401) la decide el proxy de cada
# caso de uso protegido; aquí solo se extrae el token de la cabecera.
_bearer_scheme = HTTPBearer(auto_error=False)


def bearer_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> str | None:
    """Dependencia de FastAPI: devuelve el token Bearer o None si no vino."""
    return credentials.credentials if credentials else None
