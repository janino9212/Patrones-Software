from fastapi import APIRouter, HTTPException, status
from src.shared.security import JWTManager
from src.shared.auth_schemas import LoginRequest, TokenResponse

router = APIRouter()

FAKE_USER = {"username": "admin", "password": "admin123"}

@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest):
    if credentials.username != FAKE_USER["username"] or credentials.password != FAKE_USER["password"]:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")

    try:
        token = JWTManager().create_access_token(username=credentials.username)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    return TokenResponse(access_token=token)