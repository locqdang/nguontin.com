from app.core.security import (
    generate_email_login_code,
    hash_email_login_code,
    verify_email_login_code,
)


def test_generate_email_login_code_returns_six_digits() -> None:
    code = generate_email_login_code()

    assert len(code) == 6
    assert code.isdigit()


def test_hash_email_login_code_is_not_plaintext() -> None:
    code_hash = hash_email_login_code("123456")

    assert code_hash != "123456"
    assert len(code_hash) == 64


def test_verify_email_login_code_accepts_matching_code() -> None:
    code_hash = hash_email_login_code("123456")

    assert verify_email_login_code("123456", code_hash) is True


def test_verify_email_login_code_rejects_non_matching_code() -> None:
    code_hash = hash_email_login_code("123456")

    assert verify_email_login_code("654321", code_hash) is False
