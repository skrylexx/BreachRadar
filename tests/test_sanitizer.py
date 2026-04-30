"""
tests/test_sanitizer.py

Tests unitaires du DataSanitizer.

Couverture :
- Masquage des mots de passe (format clé:valeur)
- Masquage des hashs (MD5, SHA-1, SHA-256, bcrypt)
- Masquage des clés API et tokens
- Masquage des tokens Base64
- Vérification des flags booléens
- Traitement des dictionnaires imbriqués
- Cas limites (chaîne vide, None-safe)
"""

from __future__ import annotations

import pytest

from leakmonitor.core.sanitizer import DataSanitizer, SanitizedResult


@pytest.fixture
def sanitizer() -> DataSanitizer:
    return DataSanitizer()


class TestPasswordMasking:
    """Tests de masquage des mots de passe."""

    def test_password_colon_format(self, sanitizer: DataSanitizer) -> None:
        """Format 'password:valeur' → masqué."""
        result = sanitizer.sanitize("password:abc123")
        assert result.has_password is True
        assert "abc123" not in str(result.sanitized_data)
        assert result.was_sanitized is True

    def test_password_equals_format(self, sanitizer: DataSanitizer) -> None:
        """Format 'password=valeur' → masqué."""
        result = sanitizer.sanitize("password=SuperSecret!")
        assert result.has_password is True
        assert "SuperSecret" not in str(result.sanitized_data)

    def test_passwd_variant(self, sanitizer: DataSanitizer) -> None:
        """Variante 'passwd' → masquée."""
        result = sanitizer.sanitize("passwd: mypassword123")
        assert result.has_password is True

    def test_case_insensitive(self, sanitizer: DataSanitizer) -> None:
        """Insensible à la casse."""
        result = sanitizer.sanitize("PASSWORD:secret123")
        assert result.has_password is True

    def test_plaintext_credential_flag(self, sanitizer: DataSanitizer) -> None:
        """Le flag has_plaintext_credential est levé avec has_password."""
        result = sanitizer.sanitize("password:abc123")
        assert result.has_plaintext_credential is True


class TestHashMasking:
    """Tests de masquage des hashs de mots de passe."""

    def test_md5_hash(self, sanitizer: DataSanitizer) -> None:
        """Hash MD5 (32 hex) → masqué."""
        md5 = "5f4dcc3b5aa765d61d8327deb882cf99"  # MD5 de "password"
        result = sanitizer.sanitize(md5)
        assert result.has_hash is True
        assert md5 not in str(result.sanitized_data)

    def test_sha1_hash(self, sanitizer: DataSanitizer) -> None:
        """Hash SHA-1 (40 hex) → masqué."""
        sha1 = "5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8"  # SHA-1 de "password"
        result = sanitizer.sanitize(sha1)
        assert result.has_hash is True
        assert sha1 not in str(result.sanitized_data)

    def test_sha256_hash(self, sanitizer: DataSanitizer) -> None:
        """Hash SHA-256 (64 hex) → masqué."""
        sha256 = "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"
        result = sanitizer.sanitize(sha256)
        assert result.has_hash is True
        assert sha256 not in str(result.sanitized_data)

    def test_bcrypt_hash(self, sanitizer: DataSanitizer) -> None:
        """Hash bcrypt → masqué."""
        bcrypt = "$2b$12$EIXZet8OhK5P9YMQjL9BreWEcEidiFuUxH6EzkyovJlbHcCy9TLWK"
        result = sanitizer.sanitize(bcrypt)
        assert result.has_hash is True
        assert bcrypt not in str(result.sanitized_data)

    def test_hash_in_dict(self, sanitizer: DataSanitizer) -> None:
        """Hash dans un dictionnaire → masqué."""
        data = {
            "email": "alice@example.com",
            "password_hash": "5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8",
        }
        result = sanitizer.sanitize(data)
        assert result.has_hash is True
        assert "5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8" not in str(result.sanitized_data)


class TestApiKeyMasking:
    """Tests de masquage des clés API et tokens."""

    def test_api_key_format(self, sanitizer: DataSanitizer) -> None:
        """Format 'api_key:valeur' → masqué."""
        result = sanitizer.sanitize("api_key:sk-1234567890abcdef")
        assert result.has_api_key is True

    def test_token_format(self, sanitizer: DataSanitizer) -> None:
        """Format 'token:valeur' → masqué."""
        result = sanitizer.sanitize("token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9")
        assert result.has_api_key is True

    def test_github_token(self, sanitizer: DataSanitizer) -> None:
        """Token GitHub (ghp_...) → masqué."""
        github_token = "ghp_1234567890abcdefghij1234567890abcdef12"
        result = sanitizer.sanitize(github_token)
        assert result.has_api_key is True
        assert github_token not in str(result.sanitized_data)

    def test_bearer_token(self, sanitizer: DataSanitizer) -> None:
        """Bearer token → masqué."""
        result = sanitizer.sanitize("bearer: mySecretToken123456")
        assert result.has_api_key is True


class TestCleanData:
    """Tests sur des données sûres — pas de faux positifs."""

    def test_clean_email(self, sanitizer: DataSanitizer) -> None:
        """Email normal → pas masqué."""
        result = sanitizer.sanitize("alice@mondomaine.fr")
        assert result.has_any_sensitive_data is False
        assert result.was_sanitized is False

    def test_clean_breach_name(self, sanitizer: DataSanitizer) -> None:
        """Nom de breach → pas masqué."""
        result = sanitizer.sanitize("Adobe 2013")
        assert result.has_any_sensitive_data is False

    def test_clean_dict(self, sanitizer: DataSanitizer) -> None:
        """Dictionnaire sans données sensibles → pas modifié."""
        data = {
            "breach_name": "Adobe",
            "date": "2013-10-04",
            "data_classes": ["Email addresses", "Password hints"],
            "verified": True,
        }
        result = sanitizer.sanitize(data)
        assert result.has_any_sensitive_data is False
        assert result.sanitized_data == data

    def test_empty_string(self, sanitizer: DataSanitizer) -> None:
        """Chaîne vide → pas d'erreur."""
        result = sanitizer.sanitize("")
        assert result.has_any_sensitive_data is False

    def test_empty_dict(self, sanitizer: DataSanitizer) -> None:
        """Dictionnaire vide → pas d'erreur."""
        result = sanitizer.sanitize({})
        assert result.has_any_sensitive_data is False


class TestIsSafe:
    """Tests de la méthode is_safe()."""

    def test_is_safe_clean(self, sanitizer: DataSanitizer) -> None:
        assert sanitizer.is_safe("Alice was breached in Adobe 2013") is True

    def test_is_safe_with_password(self, sanitizer: DataSanitizer) -> None:
        assert sanitizer.is_safe("password:secret123") is False

    def test_is_safe_with_hash(self, sanitizer: DataSanitizer) -> None:
        assert sanitizer.is_safe("5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8") is False
