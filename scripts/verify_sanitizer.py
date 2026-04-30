"""
scripts/verify_sanitizer.py

Script de vérification manuelle du DataSanitizer.
À lancer avant chaque release ou après modification du sanitizer.

Usage : uv run python scripts/verify_sanitizer.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour l'import
sys.path.insert(0, str(Path(__file__).parent.parent))

from leakmonitor.core.sanitizer import DataSanitizer

sanitizer = DataSanitizer()

# Format : (texte_input, doit_être_sensible, label_du_test)
TEST_CASES: list[tuple[str | dict, bool, str]] = [
    # ── Mots de passe ──────────────────────────────────────────────────────
    ("password:abc123",                True,  "password:valeur"),
    ("password=SuperSecret!",          True,  "password=valeur"),
    ("PASSWORD:secret123",             True,  "PASSWORD majuscule"),
    ("passwd: monpass",                True,  "passwd variant"),
    ("pwd=hunter2",                    True,  "pwd variant"),

    # ── Hashs ───────────────────────────────────────────────────────────────
    ("5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8",                          True, "SHA-1 (40 hex)"),
    ("5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",  True, "SHA-256 (64 hex)"),
    ("5f4dcc3b5aa765d61d8327deb882cf99",                                   True, "MD5 (32 hex)"),
    ("$2b$12$EIXZet8OhK5P9YMQjL9BreWEcEidiFuUxH6EzkyovJlbHcCy9TLWK",    True, "bcrypt hash"),

    # ── Tokens / Clés API ────────────────────────────────────────────────────
    ("ghp_1234567890abcdefghij1234567890abcdef12",  True, "GitHub token"),
    ("api_key=sk-prod-xxxxxxxxxxxxx",               True, "api_key format"),
    ("token=eyJhbGciOiJIUzI1NiJ9",                 True, "bearer token"),
    ("secret=my_super_secret_value_123",            True, "secret format"),

    # ── Dict imbriqué ────────────────────────────────────────────────────────
    (
        {"email": "alice@test.com", "hash": "5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8"},
        True,
        "hash dans dict",
    ),
    (
        {"email": "alice@test.com", "breach": "Adobe 2013"},
        False,
        "dict propre",
    ),

    # ── Données propres — pas de faux positifs ───────────────────────────────
    ("alice@mondomaine.fr",             False, "email propre"),
    ("Adobe 2013",                      False, "nom de breach"),
    ("Email addresses, Passwords",      False, "data_classes texte"),
    ("LockBit 3.0",                     False, "nom de groupe ransom"),
    ("2024-03-15",                      False, "date"),
    ("France",                          False, "pays"),
    ("500GB",                           False, "taille données"),
    ("",                                False, "chaîne vide"),
    ({},                                False, "dict vide"),
]


def run_tests() -> bool:
    print("=" * 60)
    print("  LeakMonitor — Vérification Sanitizer")
    print("=" * 60)
    print()

    passed = 0
    failed = 0
    errors: list[str] = []

    for text, should_be_sensitive, label in TEST_CASES:
        try:
            result = sanitizer.sanitize(text)  # type: ignore[arg-type]
            is_sensitive = result.has_any_sensitive_data

            if is_sensitive == should_be_sensitive:
                status = "✅ PASS"
                passed += 1
            else:
                status = "❌ FAIL"
                failed += 1
                direction = "faux positif" if is_sensitive else "faux négatif"
                errors.append(f"  [{label}] → {direction}")

            print(f"  {status}  [{label:<40}] sensitive={is_sensitive}")

        except Exception as e:
            print(f"  💥 ERREUR  [{label:<40}] Exception: {e}")
            failed += 1
            errors.append(f"  [{label}] → Exception: {e}")

    print()
    print("─" * 60)
    print(f"  Résultat : {passed} passés / {passed + failed} total")

    if errors:
        print()
        print("  ❌ Échecs :")
        for err in errors:
            print(err)
        print()
        print("  ⛔ SANITIZER NON CONFORME — Ne pas déployer")
        return False
    else:
        print()
        print("  ✅ Sanitizer conforme — Tous les cas couverts")
        return True


if __name__ == "__main__":
    ok = run_tests()
    sys.exit(0 if ok else 1)
