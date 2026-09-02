from src.shared.database import DatabaseConnection, get_db


def test_database_connection_is_singleton():
    """El patrón Singleton debe devolver siempre la misma instancia."""
    first_instance = DatabaseConnection()
    second_instance = DatabaseConnection()

    assert first_instance is second_instance


def test_database_connection_exposes_a_single_engine():
    connection = DatabaseConnection()

    assert connection.engine is not None
    # El engine también debe ser el mismo entre instancias "distintas" del Singleton.
    assert connection.engine is DatabaseConnection().engine


def test_get_db_yields_a_session_and_closes_it_afterwards():
    db_generator = get_db()

    session = next(db_generator)
    assert session is not None

    # Al agotar el generador se ejecuta el `finally` (session.close()) sin errores.
    try:
        next(db_generator)
    except StopIteration:
        pass
    else:
        raise AssertionError("Se esperaba que el generador de get_db terminara tras un solo yield")
