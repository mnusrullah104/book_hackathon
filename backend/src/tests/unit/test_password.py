import pytest
from ...services.auth import hash_password, verify_password


def test_hash_password_produces_bcrypt_hash():
    """Test that hash_password produces a bcrypt hash starting with $2b$."""
    plain_password = "SecurePass123"
    hashed = hash_password(plain_password)

    # Bcrypt hashes start with $2b$
    assert hashed.startswith("$2b$")
    # Hashed password should be different from plain text
    assert hashed != plain_password
    # Bcrypt hashes are typically 60 characters
    assert len(hashed) == 60


def test_hash_password_is_deterministic_for_same_input():
    """Test that hashing the same password twice produces different salts but valid hashes."""
    password = "SamePassword123"

    hash1 = hash_password(password)
    hash2 = hash_password(password)

    # Hashes should be different due to random salt
    assert hash1 != hash2

    # But both should be valid bcrypt hashes
    assert hash1.startswith("$2b$")
    assert hash2.startswith("$2b$")


def test_verify_password_correct_password_returns_true():
    """Test that verify_password returns True for correct password."""
    plain_password = "CorrectPass123"
    hashed = hash_password(plain_password)

    result = verify_password(plain_password, hashed)
    assert result is True


def test_verify_password_incorrect_password_returns_false():
    """Test that verify_password returns False for incorrect password."""
    plain_password = "CorrectPass123"
    wrong_password = "WrongPass456"
    hashed = hash_password(plain_password)

    result = verify_password(wrong_password, hashed)
    assert result is False


def test_verify_password_empty_password_returns_false():
    """Test that verify_password returns False for empty password."""
    plain_password = "SomePass123"
    hashed = hash_password(plain_password)

    result = verify_password("", hashed)
    assert result is False


def test_verify_password_none_password_returns_false():
    """Test that verify_password returns False for None password."""
    plain_password = "SomePass123"
    hashed = hash_password(plain_password)

    result = verify_password(None, hashed)
    assert result is False


def test_hash_and_verify_roundtrip():
    """Test complete roundtrip: hash a password and verify it matches."""
    passwords = [
        "Simple1",
        "Complex!@#$%^&*()",
        "WithNumbers123456",
        "MixedCaseAbCdEf",
        "Spaces and special !@# $%^",
    ]

    for password in passwords:
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True
        assert verify_password(password + "wrong", hashed) is False
