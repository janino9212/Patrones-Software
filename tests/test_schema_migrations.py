from sqlalchemy import create_engine, inspect, text

from src.shared.schema_migrations import apply_added_columns


def _columns(engine, table: str) -> set[str]:
    return {column["name"] for column in inspect(engine).get_columns(table)}


def test_adds_status_to_a_routes_table_created_before_the_column_existed():
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as connection:
        connection.execute(text("CREATE TABLE distribution_routes (id INTEGER PRIMARY KEY)"))
        connection.execute(text("INSERT INTO distribution_routes (id) VALUES (1)"))

    apply_added_columns(engine)
    apply_added_columns(engine)  # idempotente

    assert "status" in _columns(engine, "distribution_routes")
    with engine.connect() as connection:
        status = connection.execute(text("SELECT status FROM distribution_routes")).scalar()
    assert status == "planned"


def test_does_nothing_when_the_table_does_not_exist_yet():
    engine = create_engine("sqlite:///:memory:")

    apply_added_columns(engine)

    assert inspect(engine).get_table_names() == []
