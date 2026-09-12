import os
import threading
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

    def create_access_token(self, username: str) -> str:
        # si ya hay un token activo y todavía no expiró, no se genera otro
        existing_token = self._active_tokens.get(username)
        if existing_token and self._is_valid(existing_token):
            raise ValueError("Ya existe una sesión activa para este usuario")

        expire = datetime.now(timezone.utc) + timedelta(minutes=self._expire_minutes)
        payload = {"sub": username, "exp": expire}
        token = jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

        self._active_tokens[username] = token
        return token

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
        except JWTError:
            raise ValueError("Token inválido o expirado")

    def _is_valid(self, token: str) -> bool:
        try:
            self.decode_token(token)
            return True
        except ValueError:
            return False

    def invalidate_token(self, username: str) -> None:
        """Para un futuro endpoint de logout."""
        self._active_tokens.pop(username, None)