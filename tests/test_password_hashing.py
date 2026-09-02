from src.shared.password_hashing import hash_password, verify_password


def test_hash_password_does_not_store_plain_text():
    hashed = hash_password("mi-clave-secreta")

    assert hashed != "mi-clave-secreta"


def test_verify_password_returns_true_for_correct_password():
    hashed = hash_password("mi-clave-secreta")

    assert verify_password("mi-clave-secreta", hashed) is True


def test_verify_password_returns_false_for_incorrect_password():
    hashed = hash_password("mi-clave-secreta")

    assert verify_password("clave-equivocada", hashed) is False


def test_hash_password_generates_different_hashes_for_same_password():
    # bcrypt usa un salt aleatorio por llamada, así que dos hashes de la
    # misma contraseña no deben coincidir.
    first_hash = hash_password("misma-clave")
    second_hash = hash_password("misma-clave")

    assert first_hash != second_hash
