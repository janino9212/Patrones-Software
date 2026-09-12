import pytest

from src.shared.security import JWTManager


@pytest.fixture
def jwt_manager():
    manager = JWTManager()
    yield manager
    # Limpieza: evita que una sesión activa de un test se filtre a otro,
    # dado que JWTManager es un Singleton con estado compartido.
    manager.invalidate_token("user_singleton_test")
    manager.invalidate_token("user_duplicate_test")


def test_jwt_manager_is_singleton(jwt_manager):
    assert jwt_manager is JWTManager()


def test_create_and_decode_access_token_roundtrip(jwt_manager):
    token = jwt_manager.create_access_token("user_singleton_test")

    payload = jwt_manager.decode_token(token)

    assert payload["sub"] == "user_singleton_test"


def test_create_access_token_twice_for_same_user_raises_value_error(jwt_manager):
    jwt_manager.create_access_token("user_duplicate_test")

    with pytest.raises(ValueError):
        jwt_manager.create_access_token("user_duplicate_test")


def test_decode_invalid_token_raises_value_error(jwt_manager):
    with pytest.raises(ValueError):
        jwt_manager.decode_token("token-que-no-es-un-jwt-valido")


def test_invalidate_token_allows_login_again(jwt_manager):
    jwt_manager.create_access_token("user_singleton_test")

    jwt_manager.invalidate_token("user_singleton_test")

    # Tras invalidar la sesión, debe poder generarse un nuevo token sin error.
    new_token = jwt_manager.create_access_token("user_singleton_test")
    assert new_token
