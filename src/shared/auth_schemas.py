from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.shared.password_hashing import MAX_PASSWORD_BYTES, is_within_bcrypt_limit


class LoginRequest(BaseModel):
    username: str = Field(max_length=50)
    # Sin validar el límite de bcrypt aquí: una contraseña demasiado larga
    # simplemente no coincide y responde 401, igual que cualquier otra.
    password: str = Field(max_length=1024)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str | None = None


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_.-]+$")
    password: str = Field(min_length=6, max_length=MAX_PASSWORD_BYTES)

    @field_validator("password")
    @classmethod
    def _fits_in_bcrypt(cls, value: str) -> str:
        # El límite de bcrypt es en bytes: las tildes y la ñ ocupan dos.
        if not is_within_bcrypt_limit(value):
            raise ValueError(
                f"La contraseña no puede ocupar más de {MAX_PASSWORD_BYTES} bytes"
            )
        return value


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str


class MessageResponse(BaseModel):
    message: str
