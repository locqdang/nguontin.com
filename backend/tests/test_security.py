from app.core.security import hash_password, verify_password


def test_hash_password_returns_argon2_hash() -> None:
    password_hash = hash_password("mat-khau-rat-an-toan")

    assert password_hash.startswith("$argon2id$")
    assert password_hash != "mat-khau-rat-an-toan"


def test_verify_password_accepts_matching_password() -> None:
    password_hash = hash_password("nguontin-123")

    assert verify_password("nguontin-123", password_hash) is True


def test_verify_password_rejects_non_matching_password() -> None:
    password_hash = hash_password("nguontin-123")

    assert verify_password("sai-mat-khau", password_hash) is False
