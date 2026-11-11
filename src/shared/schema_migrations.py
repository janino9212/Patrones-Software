import logging

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

logger = logging.getLogger("scm.database")

# Columnas agregadas a tablas que ya existían en bases desplegadas.
# `Base.metadata.create_all` crea tablas nuevas pero no altera las existentes,
# y el proyecto no usa Alembic; esta lista cubre esos casos puntuales.
# (tabla, columna, definición SQL). Solo constantes del código, nunca entrada
# del usuario.
_ADDED_COLUMNS: tuple[tuple[str, str, str], ...] = (
    ("distribution_routes", "status", "VARCHAR(20) NOT NULL DEFAULT 'planned'"),
)


def apply_added_columns(engine: Engine) -> None:
    """Agrega las columnas faltantes de _ADDED_COLUMNS. Es idempotente."""
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    for table, column, definition in _ADDED_COLUMNS:
        if table not in existing_tables:
            continue
        columns = {col["name"] for col in inspector.get_columns(table)}
        if column in columns:
            continue
        with engine.begin() as connection:
            connection.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {definition}"))
        logger.info("Columna %s.%s agregada", table, column)
