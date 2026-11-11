import bcrypt

# bcrypt solo procesa los primeros 72 bytes y, desde la versión 5, rechaza
# cualquier contraseña más larga en vez de truncarla.
MAX_PASSWORD_BYTES = 72


def is_within_bcrypt_limit(plain_password: str) -> bool:
    return len(plain_password.encode("utf-8")) <= MAX_PASSWORD_BYTES


def hash_password(plain_password: str) -> str:
    """Genera un hash bcrypt (con salt aleatorio) de la contraseña en texto plano."""
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compara una contraseña en texto plano contra su hash bcrypt almacenado.

    Una contraseña que supera el límite de bcrypt no puede ser la correcta:
    se responde False en lugar de dejar escapar el ValueError."""
    if not is_within_bcrypt_limit(plain_password):
        return False
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
