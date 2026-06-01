"""
breachradar/core/sanitizer.py

Couche de nettoyage des données sensibles.

RÈGLE FONDAMENTALE :
Ce module est appelé IMMÉDIATEMENT après réception de toute réponse d'API
externe. Aucune donnée sensible ne doit transiter au-delà de ce point.

Données sanitisées :
- Mots de passe (en clair ou en format "password:value")
- Hashs (MD5, SHA-1, SHA-256, bcrypt)
- Clés API et tokens
- Chaînes Base64 potentiellement sensibles

Exception : les données RansomLook sont publiques par nature et ne sont
PAS passées par ce sanitizer.
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
    Résultat de la sanitisation — contient uniquement des flags booléens,
    jamais les données sensibles elles-mêmes.
    """

    # Flags détectés
    has_password: bool = False
    has_hash: bool = False
    has_api_key: bool = False
    has_plaintext_credential: bool = False
    has_base64_token: bool = False

    # Données sûres (données sensibles remplacées par des marqueurs)
    sanitized_data: Any = None

    # Métadonnées
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
    Sanitizer principal — masque toutes les données sensibles.

    Usage :
        sanitizer = DataSanitizer()
        result = sanitizer.sanitize(raw_api_response)
        # result.has_password → True si un mot de passe a été détecté
        # result.sanitized_data → données sans les valeurs sensibles
    """

    # Patterns de détection des données sensibles
    # Ordre important : du plus spécifique au plus général
    SENSITIVE_PATTERNS: list[tuple[str, str, str]] = [
        # (nom_flag, regex_pattern, marqueur_remplacement)
        # Mots de passe en format clé:valeur
        (
            "has_password",
            r"(?i)(?:password[s]?|passwd|pwd|pass)\s*[:=]\s*\S+",
            "[PASSWORD MASQUÉ]",
        ),
        # Hash bcrypt (priorité haute car spécifique)
        (
            "has_hash",
            r"\$2[ayb]\$.{56}",
            "[HASH BCRYPT MASQUÉ]",
        ),
        # Hash SHA-256 (64 caractères hex)
        (
            "has_hash",
            r"\b[a-f0-9]{64}\b",
            "[HASH SHA-256 MASQUÉ]",
        ),
        # Hash SHA-1 (40 caractères hex)
        (
            "has_hash",
            r"\b[a-f0-9]{40}\b",
            "[HASH SHA-1 MASQUÉ]",
        ),
        # Hash MD5 (32 caractères hex)
        (
            "has_hash",
            r"\b[a-f0-9]{32}\b",
            "[HASH MD5 MASQUÉ]",
        ),
        # Clés API et tokens en format clé:valeur
        (
            "has_api_key",
            r"(?i)(?:api[_-]?key|token|secret|bearer|auth)\s*[:=]\s*\S+",
            "[CLÉ API MASQUÉE]",
        ),
        # Tokens GitHub (ghp_, ghs_, ghx_, etc.)
        (
            "has_api_key",
            r"\bgh[psouxr]_[A-Za-z0-9]{36,}\b",
            "[TOKEN GITHUB MASQUÉ]",
        ),
        # Chaînes Base64 longues (potentiellement des tokens)
        # Seuil : 40+ caractères pour éviter les faux positifs
        (
            "has_base64_token",
            r"\b[A-Za-z0-9+/]{40,}={0,2}\b",
            "[TOKEN BASE64 MASQUÉ]",
        ),
    ]

    def __init__(self) -> None:
        # Pré-compiler les regex pour les performances
        self._compiled_patterns = [
            (flag, re.compile(pattern), replacement)
            for flag, pattern, replacement in self.SENSITIVE_PATTERNS
        ]

    def sanitize(self, raw: dict | list | str) -> SanitizedResult:
        """
        Point d'entrée principal du sanitizer.

        Args:
            raw: Données brutes reçues de l'API (dict, list ou str)

        Returns:
            SanitizedResult avec les flags et les données nettoyées
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
        """Sanitise récursivement un dictionnaire."""
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
        Applique tous les patterns de sanitisation sur une chaîne.
        Met à jour les flags du SanitizedResult en cas de match.
        """
        sanitized = text
        for flag_name, pattern, replacement in self._compiled_patterns:
            if pattern.search(sanitized):
                # Mettre à jour le flag correspondant
                setattr(result, flag_name, True)
                if flag_name == "has_password":
                    result.has_plaintext_credential = True
                result.patterns_matched.append(pattern.pattern[:30])
                # Remplacer la valeur sensible
                sanitized = pattern.sub(replacement, sanitized)

        return sanitized

    @staticmethod
    def purge_sensitive(data: str | bytes) -> None:
        """
        Écrase une chaîne sensible en mémoire avant de la libérer.

        ATTENTION : En Python, les str sont immutables et interned.
        Cette fonction fait de son mieux mais n'est pas une garantie absolue.
        Pour une sécurité maximale, utiliser des bytearray mutables dès le début.

        Args:
            data: Chaîne ou bytes contenant des données sensibles
        """
        try:
            if isinstance(data, str) and data:
                # Tenter d'écraser le buffer interne (best effort)
                ctypes.memset(id(data), 0, len(data))
        except Exception:
            pass  # L'échec de la purge mémoire ne doit pas bloquer l'exécution
        finally:
            del data
            gc.collect()

    def is_safe(self, text: str) -> bool:
        """
        Vérifie rapidement si une chaîne contient des données sensibles.

        Args:
            text: Texte à vérifier

        Returns:
            True si aucune donnée sensible détectée
        """
        return all(not pattern.search(text) for _, pattern, _ in self._compiled_patterns)
