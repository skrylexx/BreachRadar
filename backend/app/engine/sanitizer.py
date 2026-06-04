"""
breachradar/core/sanitizer.py

Sensitive data cleaning layer.

FUNDAMENTAL RULE:
This module is called IMMEDIATELY after receiving any API response
external. No sensitive data should pass beyond this point.

Sanitized data:
- Passwords (in plain text or in "password:value" format)
- Hashes (MD5, SHA-1, SHA-256, bcrypt)
- API keys and tokens
- Potentially sensitive Base64 strings

Exception: RansomLook data is public by nature and is not
NOT passed through this sanitizer.
"""

from __future__ import annotations

import ctypes
import gc
import logging
import re
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class SanitizedResult:
    """
    Sanitization result — contains only Boolean flags,
    never the sensitive data itself.
    """

    # Flags detected
    has_password: bool = False
    has_hash: bool = False
    has_api_key: bool = False
    has_plaintext_credential: bool = False
    has_base64_token: bool = False

    # Safe data (sensitive data replaced by markers)
    sanitized_data: Any = None

    # Metadata
    patterns_matched: list[str] = field(default_factory=list)
    was_sanitized: bool = False

    @property
    def has_any_sensitive_data(self) -> bool:
        return any(
            [
                self.has_password,
                self.has_hash,
                self.has_api_key,
                self.has_plaintext_credential,
                self.has_base64_token,
            ]
        )


class DataSanitizer:
    """
    Master Sanitizer — hides all sensitive data.

    Usage:
        sanitizer = DataSanitizer()
        result = sanitizer.sanitize(raw_api_response)
        # result.has_password → True if a password was detected
        # result.sanitized_data → data without sensitive values
    """

    # Sensitive data detection patterns
    # Important order: from most specific to most general
    SENSITIVE_PATTERNS: list[tuple[str, str, str]] = [
        # (flag_name, regex_pattern, replacement_marker)
        # Passwords in key:value format
        (
            "has_password",
            r"(?i)(?:password[s]?|passwd|pwd|pass)\s*[:=]\s*\S+",
            "[PASSWORD MASQUÉ]",
        ),
        # Hash bcrypt (high priority because specific)
        (
            "has_hash",
            r"\$2[ayb]\$.{56}",
            "[HASH BCRYPT MASQUÉ]",
        ),
        # SHA-256 hash (64 hex characters)
        (
            "has_hash",
            r"\b[a-f0-9]{64}\b",
            "[HASH SHA-256 MASQUÉ]",
        ),
        # SHA-1 hash (40 hex characters)
        (
            "has_hash",
            r"\b[a-f0-9]{40}\b",
            "[HASH SHA-1 MASQUÉ]",
        ),
        # Hash MD5 (32 hex characters)
        (
            "has_hash",
            r"\b[a-f0-9]{32}\b",
            "[HASH MD5 MASQUÉ]",
        ),
        # API keys and tokens in key:value format
        (
            "has_api_key",
            r"(?i)(?:api[_-]?key|token|secret|bearer|auth)\s*[:=]\s*\S+",
            "[CLÉ API MASQUÉE]",
        ),
        # GitHub tokens (ghp_, ghs_, ghx_, etc.)
        (
            "has_api_key",
            r"\bgh[psouxr]_[A-Za-z0-9]{36,}\b",
            "[TOKEN GITHUB MASQUÉ]",
        ),
        # Long Base64 strings (potentially tokens)
        # Threshold: 40+ characters to avoid false positives
        (
            "has_base64_token",
            r"\b[A-Za-z0-9+/]{40,}={0,2}\b",
            "[TOKEN BASE64 MASQUÉ]",
        ),
    ]

    def __init__(self) -> None:
        # Pre-compile regex for performance
        self._compiled_patterns = [
            (flag, re.compile(pattern), replacement) for flag, pattern, replacement in self.SENSITIVE_PATTERNS
        ]

    def sanitize(self, raw: dict | list | str) -> SanitizedResult:
        """
        Main entry point for the sanitizer.

        Args:
            raw: Raw data received from the API (dict, list or str)

        Returns:
            SanitizedResult with flags and sanitized data
        """
        result = SanitizedResult()

        if isinstance(raw, dict):
            result.sanitized_data = self._sanitize_dict(raw, result)
        elif isinstance(raw, list):
            result.sanitized_data = [
                self._sanitize_dict(item, result)
                if isinstance(item, dict)
                else self._sanitize_string(str(item), result)
                for item in raw
            ]
        elif isinstance(raw, str):
            result.sanitized_data = self._sanitize_string(raw, result)

        if result.has_any_sensitive_data:
            result.was_sanitized = True
            logger.debug(
                f"Sanitizer : données sensibles détectées — "
                f"flags={[k for k, v in result.__dict__.items() if k.startswith('has_') and v]}"
            )

        return result

    def _sanitize_dict(self, data: dict, result: SanitizedResult) -> dict:
        """Recursively sanitizes a dictionary."""
        sanitized: dict[Any, Any] = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = self._sanitize_string(value, result)
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_dict(value, result)
            elif isinstance(value, list):
                sanitized[key] = [
                    self._sanitize_dict(item, result)
                    if isinstance(item, dict)
                    else self._sanitize_string(str(item), result)
                    if isinstance(item, str)
                    else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        return sanitized

    def _sanitize_string(self, text: str, result: SanitizedResult) -> str:
        """
        Applies all sanitization patterns on a chain.
        Updates the SanitizedResult flags in case of a match.
        """
        sanitized = text
        for flag_name, pattern, replacement in self._compiled_patterns:
            if pattern.search(sanitized):
                # Update the corresponding flag
                setattr(result, flag_name, True)
                if flag_name == "has_password":
                    result.has_plaintext_credential = True
                result.patterns_matched.append(pattern.pattern[:30])
                # Replace sensitive value
                sanitized = pattern.sub(replacement, sanitized)

        return sanitized

    @staticmethod
    def purge_sensitive(data: str | bytes) -> None:
        """
        Overwrites a sensitive string in memory before freeing it.

        WARNING: In Python, str are immutable and interned.
        This function does its best but is not an absolute guarantee.
        For maximum security, use mutable bytearrays from the start.

        Args:
            data: String or bytes containing sensitive data
        """
        try:
            if isinstance(data, str) and data:
                # Try to overwrite the internal buffer (best effort)
                ctypes.memset(id(data), 0, len(data))
        except Exception:
            pass  # Failed memory purge should not block execution
        finally:
            del data
            gc.collect()

    def is_safe(self, text: str) -> bool:
        """
        Quickly checks if a string contains sensitive data.

        Args:
            text: Text to check

        Returns:
            True if no sensitive data detected
        """
        return all(not pattern.search(text) for _, pattern, _ in self._compiled_patterns)
