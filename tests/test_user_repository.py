from src.shared.user_repository import create_user, get_user_by_username


def test_create_user_persists_it(db_session):
    created = create_user(db_session, "usuario_repo", "hash-falso")

    assert created.id is not None
    assert created.username == "usuario_repo"


def test_get_user_by_username_finds_existing_user(db_session):
    create_user(db_session, "usuario_repo", "hash-falso")

    found = get_user_by_username(db_session, "usuario_repo")

    assert found is not None
    assert found.username == "usuario_repo"


def test_get_user_by_username_returns_none_when_not_found(db_session):
    found = get_user_by_username(db_session, "no_existe")

    assert found is None
