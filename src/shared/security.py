import os
import threading
import uuid
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from jose import jwt, JWTError

load_dotenv()

# Default solo para desarrollo local sin .env configurado.
# En producción/nube, definir JWT_SECRET_KEY en el entorno o en .env (ver .env.example).
_DEFAULT_LOCAL_SECRET_KEY = "clave-super-secreta-solo-para-desarrollo-local"


class JWTManager:
    """Singleton que centraliza JWT y controla sesiones activas por usuario."""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    print("[SINGLETON] Creando la única instancia de JWTManager")
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
                else:
                    print("[SINGLETON] Ya existía una instancia de JWTManager, se reutiliza")
        else:
            print("[SINGLETON] Ya existía una instancia de JWTManager, se reutiliza")
        return cls._instance

    def _initialize(self):
        self._secret_key = os.getenv("JWT_SECRET_KEY", _DEFAULT_LOCAL_SECRET_KEY)
        self._algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self._expire_minutes = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
        self._active_tokens: dict[str, str] = {}  # username -> token activo
        self._sessions_lock = threading.Lock()

    def create_access_token(self, username: str) -> str:
        """Genera un token nuevo. Si el usuario ya tenía una sesión, el token
        anterior deja de ser el activo (la sesión nueva reemplaza a la vieja)."""
        expire = datetime.now(timezone.utc) + timedelta(minutes=self._expire_minutes)
        # jti: identificador único, para que dos tokens del mismo usuario
        # emitidos en el mismo segundo no sean idénticos.
        payload = {"sub": username, "exp": expire, "jti": uuid.uuid4().hex}
        token = jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

        with self._sessions_lock:
            self._active_tokens[username] = token
        return token

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
        except JWTError:
            raise ValueError("Token inválido o expirado")

    def decode_active_token(self, token: str) -> dict:
        """Como decode_token, pero además exige que el token sea la sesión
        activa del usuario: uno reemplazado por otro login o cerrado con
        logout se rechaza aunque su firma y vencimiento sigan siendo válidos."""
        payload = self.decode_token(token)
        username = payload.get("sub")
        if not isinstance(username, str) or self._active_tokens.get(username) != token:
            raise ValueError("La sesión ya no está activa")
        return payload

    def invalidate_token(self, username: str, token: str | None = None) -> None:
        """Cierra la sesión del usuario (logout).

        Si se indica `token`, solo se cierra cuando ese sigue siendo el
        activo: así un logout con un token viejo no tumba la sesión que
        el mismo usuario abrió después con otro login."""
        with self._sessions_lock:
            if token is None or self._active_tokens.get(username) == token:
                self._active_tokens.pop(username, None)
