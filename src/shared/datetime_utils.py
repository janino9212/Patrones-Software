from datetime import datetime, timezone


def ensure_utc(value: datetime) -> datetime:
    """Devuelve la fecha con zona horaria UTC.

    Todas las fechas se guardan en UTC, pero SQLite las devuelve sin zona
    (Postgres sí la conserva). Sin ella, la API las serializa sin sufijo y el
    navegador las interpreta como hora local."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
