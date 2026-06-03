# SECURITY.md — BreachRadar Security Procedures

> **Critical Document** — Read before any API key manipulation.
> Revised: 2026-04-30 | Version: 1.0

---

## Risk Context

This project handles **real-cost API keys** (some > €100/month) and accesses sensitive security data. An API key leak can lead to:

- Unauthorized billing on your account (especially IntelX, Dehashed)
- Exposure of your monitoring data to a third party
- Invalidation of your tokens by providers (immediate loss of access)

---

## 1. Absolute Rules (Non-negotiable)

```
❌ NEVER put API keys in a versioned file (git commit)
❌ NEVER put API keys in application logs
❌ NEVER put API keys in publicly exposed Docker variables
❌ NEVER share API keys via email or unencrypted messaging
❌ NEVER put API keys in a generated report

✅ Only in .env (gitignored)
✅ Database encryption via Fernet for keys configured from the WebUI
✅ One key = one use = one project
```

---

## 2. Checklist Before First Launch

### 2.1 .gitignore Verification

```bash
# Ensure .env is properly ignored
cat .gitignore | grep "^\.env$"
# Should display: .env

# Verify that no key is already tracked by git
git ls-files | grep "\.env"
# Should return EMPTY — if not, see section 5.2
```

### 2.2 Verification Before Each Commit

```bash
# Scan the repo for potential secrets
# (to be run manually or via pre-commit hook)
git diff --cached | grep -iE "(api[_-]?key|token|secret|password|passwd)\s*[:=]\s*\S+"
# Should return EMPTY

# Alternative with detect-secrets (recommended)
pip install detect-secrets
detect-secrets scan > .secrets.baseline
detect-secrets audit .secrets.baseline
```

### 2.3 .env Validation

```bash
# Verify that .env exists and is not empty
test -f .env && echo "OK" || echo "MISSING — copy .env.example"

# Verify that TARGET_DOMAIN is configured
grep "^TARGET_DOMAIN=" .env | grep -v "=mydomain.com" | grep -v "=$"
# Should display your real domain

# Scan .env for non-empty keys
grep -E "^[A-Z_]+=.+$" .env | grep -v "^#" | wc -l
# Displays the number of configured variables
```

---

## 3. API Key Management by Service

### 3.1 Risk Table

| Service | Cost if Compromised | Revocation | Monitoring |
|---|---|---|---|
| **HIBP** | ~3.50 USD/month max | Immediate via dashboard | Email if abnormal usage |
| **GitHub Token** | €0 (read-only) | Settings → Tokens | GitHub audit log |
| **URLScan** | €0 (free) | URLScan dashboard | — |
| **OTX AlienVault** | €0 (free) | OTX dashboard | — |
| **LeakCheck** | ~50 USD/month max | LeakCheck dashboard | Usage alerts |
| **Dehashed** | ~180 USD/month max | Dehashed dashboard | Check logs |
| **IntelX** | **~500 EUR/month** ⚠️ | Contact support | **CRITICAL — monitor** |
| **Shodan** | ~65 USD (one-time) | Shodan dashboard | — |
| **Telegram** | €0 | Revoke session | Telegram sessions |

> **IntelX is the most financially risky service.** Configure spending alerts if your provider allows it.

### 3.2 Principle of Least Privilege

For each token, grant **only the necessary rights**:

```
GitHub Token   → Scopes: public_repo (read-only ONLY)
                 ❌ Do not check: repo, admin, write:*, delete:*

GitLab Token   → Scopes: read_api ONLY
                 ❌ Do not check: write_repository, api (full)

URLScan        → Permission: Search (read-only)
                 ❌ Do not check: Submit scans

Shodan         → Standard API key (no admin rights)
```

---

## 4. Incident Procedures

### 4.1 Suspected Compromised API Key

```
Emergency sequence (< 5 minutes):

1. REVOKE the key immediately (before any investigation)
   → Do not wait to confirm compromise
   → An unnecessary revocation is less serious than an active compromised key

2. GENERATE a new key (new secret, new value)

3. UPDATE the local .env (replace the old value)

4. VERIFY the usage logs of the old key (if the service allows it)
   → Identify abnormal requests

5. NOTE the incident: date, service, concerned key, suspected vector

6. If IntelX or Dehashed compromised → contact support to report
   potential fraudulent usage
```

### 4.2 Secret Found in a Git Commit

```bash
# 1. Do not panic — but act fast

# 2. Revoke the key IMMEDIATELY (see 4.1)

# 3. Clean git history (if public or shared repo)
#    CAUTION: history rewriting — coordinate with collaborators

# Option A: git filter-branch (deprecated but universal)
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch .env' \
  --prune-empty --tag-name-filter cat -- --all

# Option B: BFG Repo Cleaner (recommended, faster)
# https://rtyley.github.io/bfg-repo-cleaner/
java -jar bfg.jar --delete-files .env

# 4. Force-push (DANGEROUS — confirm with team)
git push origin --force --all
git push origin --force --tags

# 5. Invalidate existing clones (GitHub: contact support)
```

### 4.3 Generated Report Containing Unexpected Data

```bash
# 1. Delete the report immediately
rm reports/<suspect_file>

# 2. Check other reports from the same scan
ls -la reports/

# 3. Analyze what "leaked" using grep
grep -rE "(password|hash|[a-f0-9]{40})" reports/
# If result is not empty → critical bug in the sanitizer → open an issue

# 4. Never transmit the suspect report — purge it
```

---

## 5. Secure Development Environment Configuration

### 5.1 Pre-commit Hooks (Strongly Recommended)

```bash
# Install pre-commit
pip install pre-commit

# Create .pre-commit-config.yaml at root
```

`.pre-commit-config.yaml` content:

```yaml
repos:
  # Secret detection
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']

  # Verify .env is not committed
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: detect-private-key      # Detects RSA/SSH private keys
      - id: no-commit-to-branch
        args: ['--branch', 'main']  # Forbids direct commits to main

  # Python Linter
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff
      - id: ruff-format
```

```bash
# Activate hooks
pre-commit install

# Generate secrets baseline (false positives to ignore)
detect-secrets scan > .secrets.baseline

# Test on the whole repo
pre-commit run --all-files
```

### 5.2 Environment Variables — Best Practices

```bash
# GOOD: load variables for a single shell session
export HIBP_API_KEY="your_key"   # Temporary, not in history

# EVEN BETTER: use direnv (loads .env automatically)
# https://direnv.net/
# .envrc (gitignored) → direnv allow
```

### 5.3 Sensitive File Permissions

```bash
# On Linux/macOS: restrict .env permissions
chmod 600 .env
ls -la .env
# Should display: -rw------- (read/write only by owner)

# Check regularly
find . -name ".env" -perm /044 -ls
# Displays .env readable by group or others — to be fixed
```

---

## 6. Code Security Tests

### 6.1 Scan Code with Bandit

```bash
# Install bandit (Python security analyzer)
uv add --dev bandit

# Full scan of source code
cd backend && uv run bandit -r app/ -ll -f txt

# Detailed report in HTML
cd backend && uv run bandit -r app/ -f html -o security_report.html

# Codes to monitor particularly:
# B105, B106, B107 → hardcoded passwords
# B501, B502       → SSL verification disabled
# B603, B604       → shell injection
# B608             → SQL injection (no SQL here, but good reflex)
```

### 6.2 Scan Dependencies with Safety

```bash
# Check dependencies for known CVEs
pip install safety
safety check

# Via uv (export requirements first)
uv pip compile pyproject.toml -o /tmp/req.txt
safety check -r /tmp/req.txt
```

### 6.3 Run BreachRadar Security Tests

```bash
# Unit security non-regression tests
cd backend && uv run pytest tests/test_security.py -v

# Expected results:
# PASSED  test_leak_finding_has_no_sensitive_fields
# PASSED  test_report_does_not_contain_passwords
# PASSED  test_ransom_finding_portal_url_stored_but_visible
# PASSED  test_data_integrity_flags_onion_excluded
# PASSED  test_ransom_finding_elevates_global_severity_to_critical
# PASSED  test_no_ransom_no_forced_critical
# PASSED  test_empty_scan_returns_no_severity

# Full sanitizer tests
cd backend && uv run pytest tests/test_sanitizer.py -v --tb=short

# Full coverage
cd backend && uv run pytest tests/ -v --cov=app --cov-report=term-missing
```

### 6.4 Manual Sanitizer Verification

```python
# Quick verification script (to be run before each release)
# Save as backend/scripts/verify_sanitizer.py

from app.engine.sanitizer import DataSanitizer

sanitizer = DataSanitizer()

# Critical test cases
test_cases = [
    ("password:abc123",                           True,  "password"),
    ("5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8",  True,  "sha1"),
    ("5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8", True, "sha256"),
    ("$2b$12$EIXZet8OhK5P9YMQjL9BreWEcEidiFuUxH6EzkyovJlbHcCy9TLWK",   True,  "bcrypt"),
    ("ghp_1234567890abcdefghij1234567890abcdef12",                        True,  "github_token"),
    ("api_key=sk-prod-xxxxxxxxxxxxx",              True,  "api_key"),
    ("alice@mydomain.com",                        False, "clean_email"),
    ("Adobe 2013",                                 False, "clean_breach"),
]

print("=== Sanitizer Verification ===\n")
all_ok = True
for text, should_be_sensitive, label in test_cases:
    result = sanitizer.sanitize(text)
    is_sensitive = result.has_any_sensitive_data
    status = "✅" if is_sensitive == should_be_sensitive else "❌ FAILURE"
    if is_sensitive != should_be_sensitive:
        all_ok = False
    print(f"{status} [{label}] has_sensitive={is_sensitive} (expected={should_be_sensitive})")

print(f"\n{'✅ All tests passed.' if all_ok else '❌ SOME TESTS FAILED — DO NOT DEPLOY'}")
```

```bash
# Run verification
cd backend && uv run python scripts/verify_sanitizer.py
```

---

## 7. Deployment Checklist

Before each production release or project sharing:

```
[ ] .env is in .gitignore AND is not tracked by git
[ ] git status shows no sensitive files in staged
[ ] detect-secrets scan returns no new secrets
[ ] pre-commit run --all-files passes without error
[ ] uv run pytest tests/test_security.py passes 100%
[ ] uv run bandit -r breachradar/ -ll returns no HIGH
[ ] API keys in .env have the minimum necessary permissions
[ ] API keys have a configured expiration date (if the service allows it)
[ ] A quick revocation mechanism is documented (section 4.1)
[ ] docker-compose.yml: RansomLook exposed on 127.0.0.1 only (never 0.0.0.0)
[ ] No sensitive data in generated reports (reports/)
```

---

## 8. Periodic Key Rotation

Schedule rotation based on service cost/risk:

| Service | Recommended Frequency | Action |
|---|---|---|
| GitHub Token | Every 90 days | Settings → Tokens → Regenerate |
| HIBP | Every 6 months | HIBP Dashboard → New key |
| GitLab Token | Every 90 days | Preferences → Tokens |
| IntelX | Every 3 months ⚠️ | IntelX Support |
| Dehashed | Every 6 months | Dashboard → API Key |
| LeakCheck | Every 6 months | Dashboard → API |
| URLScan | Annual | URLScan Dashboard |
| OTX | Annual | Settings → API Key |

> After each rotation: update `.env` or the WebUI administration interface, and check the API connectors dashboard.

---

## 9. Recommended Network Isolation

```bash
# Option 1: Dedicated proxy for OSINT requests
# Configure in .env:
HTTP_PROXY=socks5://127.0.0.1:1080
HTTPS_PROXY=socks5://127.0.0.1:1080

# Option 2: Dedicated VPN or VPS for BreachRadar
# Advantage: OSINT requests do not expose your real IP to third-party services

# Option 3 (development only): Local Wireguard
# → Isolates BreachRadar traffic from the rest of the machine
```

---

## 10. References

- [OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [GitHub: Scanning for secrets](https://docs.github.com/en/code-security/secret-scanning)
- [detect-secrets](https://github.com/Yelp/detect-secrets)
- [Bandit — Python Security Linter](https://bandit.readthedocs.io)
- [ANSSI — Best Practices Guide](https://www.ssi.gouv.fr/guide/recommandations-relatives-a-lauthentification-multifacteur-et-aux-mots-de-passe/)
