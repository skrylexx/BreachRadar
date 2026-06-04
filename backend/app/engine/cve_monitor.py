"""
BreachRadar WebUI — CVE monitoring engine
==============================================================
Collects, normalizes and stores vulnerabilities from NVD, OSV, GitHub and CVEFeed.
Phase 9 of TODO.md.
"""

import asyncio
import logging
from datetime import UTC, datetime, timedelta

import feedparser
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.cve import CVEAlert, CVESeverity, CVESourceType

logger = logging.getLogger(__name__)

# ─── Source Configuration ─────────────────────── ───────────────────────

NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
OSV_API_URL = "https://api.osv.dev/v1/query"
GITHUB_ADVISORIES_URL = "https://github.com/advisories.atom?query=type%3Areviewed"
CVEFEED_CRITICAL_URL = "https://cvefeed.io/rssfeed/severity/critical.xml"
CVEFEED_HIGH_URL = "https://cvefeed.io/rssfeed/severity/high.xml"

# ─── Main Engine ─────────────────────────── ────────────────────────────


class CVEMonitor:
    """
    Orchestrates the collection of CVEs from different sources.
    Manages rate-limiting and database persistence.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.client = httpx.AsyncClient(timeout=30.0, headers={"User-Agent": "BreachRadar/1.0 (Cyber-Governance-Tool)"})

    async def poll_all(self, active_categories: list[str]):
        """Starts collection for all active categories."""
        logger.info(f"Démarrage du polling CVE pour {len(active_categories)} catégories.")

        # 1. NVD collection (Rate limited)
        await self._poll_nvd(active_categories)

        # 2. Collect OSV.dev
        await self._poll_osv(active_categories)

        # 3. GitHub Advisories collection
        await self._poll_github_advisories()

        # 4. CVEFeed collection
        await self._poll_cvefeed()

        await self.db.commit()
        logger.info("Polling CVE terminé.")

    # ─── NVD (NIST) ───────────────────────────── ─────────────────────────────

    async def _poll_nvd(self, categories: list[str]):
        """Queries the NVD 2.0 API."""
        # Filter NVD categories (ex: nvd_windows, nvd_linux)
        nvd_cats = [c for c in categories if c.startswith("nvd_")]
        if not nvd_cats:
            return

        # NVD rate limit: 5 req / 30s without key, 50 req / 30s with key.
        delay = 6.1 if not settings.cve_nvd_api_key else 0.6
        headers = {}
        if settings.cve_nvd_api_key:
            headers["apiKey"] = settings.cve_nvd_api_key

        for cat in nvd_cats:
            keyword = self._get_nvd_keyword(cat)
            if not keyword:
                continue

            try:
                # We retrieve CVEs published in the last 24 hours by default
                now = datetime.now(UTC)
                start_date = (now - timedelta(days=1)).isoformat()

                params = {
                    "keywordSearch": keyword,
                    "pubStartDate": start_date,
                    "pubEndDate": now.isoformat(),
                }

                response = await self.client.get(NVD_API_URL, params=params, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    await self._process_nvd_data(data, cat)
                elif response.status_code == 429:
                    logger.warning("Rate limit NVD atteint. Pause nécessaire.")

            except Exception as e:
                logger.error(f"Erreur lors du polling NVD pour {cat}: {e}")

            await asyncio.sleep(delay)

    def _get_nvd_keyword(self, cat: str) -> str | None:
        mapping = {
            "nvd_windows": "Microsoft Windows",
            "nvd_linux": "Linux Kernel",
            "nvd_macos": "Apple macOS",
        }
        return mapping.get(cat)

    async def _process_nvd_data(self, data: dict, category: str):
        vulnerabilities = data.get("vulnerabilities", [])
        for vuln in vulnerabilities:
            cve = vuln.get("cve", {})
            cve_id = cve.get("id")
            if not cve_id:
                continue

            # Severity and score extraction
            metrics = cve.get("metrics", {})
            cvss_v31 = metrics.get("cvssMetricV31", [{}])[0].get("cvssData", {})
            score = cvss_v31.get("baseScore")
            severity_str = cvss_v31.get("baseSeverity", "UNKNOWN").upper()

            description = ""
            for desc in cve.get("descriptions", []):
                if desc.get("lang") == "en":
                    description = desc.get("value", "")
                    break

            alert = CVEAlert(
                cve_id=cve_id,
                title=f"{cve_id}: {description[:100]}...",
                description=description,
                severity=self._map_severity(severity_str),
                cvss_score=score,
                category=category,
                source_type=CVESourceType.NVD,
                url=f"https://nvd.nist.gov/vuln/detail/{cve_id}",
                published_at=datetime.fromisoformat(
                    cve.get("published", datetime.now(UTC).isoformat()).replace("Z", "+00:00")
                ),
            )
            await self._upsert_cve(alert)

    # ─── GitHub Advisories ───────────────────────── ─────────────────────────

    async def _poll_github_advisories(self):
        """Parses the GitHub Advisories Atom feed."""
        try:
            response = await self.client.get(GITHUB_ADVISORIES_URL)
            if response.status_code == 200:
                feed = feedparser.parse(response.text)
                for entry in feed.entries:
                    # Extraction of the CVE ID if present in the title or tags
                    cve_id = None
                    if "CVE-" in entry.title:
                        import re

                        match = re.search(r"CVE-\d{4}-\d+", entry.title)
                        if match:
                            cve_id = match.group(0)

                    if not cve_id:
                        cve_id = f"GHSA-{entry.id.split('/')[-1]}"

                    # Extracting the date with fallback
                    if hasattr(entry, "published_parsed") and entry.published_parsed:
                        published_at = datetime(*entry.published_parsed[:6], tzinfo=UTC)
                    elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                        published_at = datetime(*entry.updated_parsed[:6], tzinfo=UTC)
                    else:
                        published_at = datetime.now(UTC)

                    alert = CVEAlert(
                        cve_id=cve_id,
                        title=entry.title,
                        description=entry.summary,
                        severity=CVESeverity.HIGH,  # GitHub does not always give the direct score in RSS
                        category="GitHub Advisories",
                        source_type=CVESourceType.GITHUB,
                        url=entry.link,
                        published_at=published_at,
                    )
                    await self._upsert_cve(alert)
        except Exception as e:
            logger.error(f"Erreur GitHub Advisories: {e}")

    # ─── OSV (Google) ──────────────────────────── ────────────────────────────

    async def _poll_osv(self, categories: list[str]):
        """
        Queries the OSV.dev API by ecosystem.
        Use modified_id.csv to list recent IDs and GET /v1/vulns/<id> for details.
        """
        osv_cats = [c for c in categories if c.startswith("osv_")]
        for cat in osv_cats:
            ecosystem = cat.replace("osv_", "").capitalize()
            # Standardizing ecosystem names for OSV
            ecosystem_map = {
                "Npm": "npm",
                "Pypi": "PyPI",
                "Nuget": "NuGet",
                "Rubygems": "RubyGems",
                "Maven": "Maven",
                "Go": "Go",
            }
            osv_ecosystem = ecosystem_map.get(ecosystem, ecosystem)

            try:
                csv_url = f"https://storage.googleapis.com/osv-vulnerabilities/{osv_ecosystem}/modified_id.csv"
                response = await self.client.get(csv_url)
                if response.status_code != 200:
                    logger.error(f"Erreur CSV OSV pour {osv_ecosystem}: {response.status_code}")
                    continue

                # We take the 10 most recent vulnerabilities (reverse chrono)
                lines = response.text.strip().split("\n")
                latest_vulns = lines[:10]

                for line in latest_vulns:
                    if not line:
                        continue
                    parts = line.split(",")
                    if len(parts) < 2:
                        continue

                    vuln_id = parts[1].strip()
                    await self._fetch_osv_detail(vuln_id, cat)
                    # Break to avoid spamming api.osv.dev
                    await asyncio.sleep(0.2)

            except Exception as e:
                logger.error(f"Erreur OSV pour {cat}: {e}")

    async def _fetch_osv_detail(self, vuln_id: str, category: str):
        """Retrieves full details of an OSV vulnerability."""
        try:
            url = f"https://api.osv.dev/v1/vulns/{vuln_id}"
            res = await self.client.get(url)
            if res.status_code == 200:
                data = res.json()

                # Severity extraction (OSV often uses CVSS v3)
                severity_str = "UNKNOWN"
                cvss_score = None

                # Check for severity field
                if "severity" in data:
                    for s in data["severity"]:
                        if s.get("type") in ["CVSS_V3", "CVSS_V4"]:
                            # We try to parse the score from the vector or the field
                            # Note: OSV score is often absent, we can just have the vector
                            pass

                # Check for database_specific field which sometimes contains severity
                db_spec = data.get("database_specific", {})
                severity_str = db_spec.get("severity", "UNKNOWN").upper()

                alert = CVEAlert(
                    cve_id=vuln_id,
                    title=data.get("summary", vuln_id),
                    description=data.get("details", ""),
                    severity=self._map_severity(severity_str),
                    cvss_score=cvss_score,
                    category=category,
                    source_type=CVESourceType.OSV,
                    url=f"https://osv.dev/vulnerability/{vuln_id}",
                    published_at=datetime.fromisoformat(
                        data.get("published", datetime.now(UTC).isoformat()).replace("Z", "+00:00")
                    ),
                )
                await self._upsert_cve(alert)
        except Exception as e:
            logger.error(f"Erreur détail OSV {vuln_id}: {e}")

    # ─── Uses ─────────────────────────────── ────────────────────────────────

    def _map_severity(self, sev: str) -> CVESeverity:
        try:
            return CVESeverity(sev.upper())
        except ValueError:
            return CVESeverity.UNKNOWN

    async def _upsert_cve(self, alert: CVEAlert):
        """Inserts or updates a CVE in database."""
        # Check if it already exists
        stmt = select(CVEAlert).where(CVEAlert.cve_id == alert.cve_id)
        result = await self.db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            existing.title = alert.title
            existing.description = alert.description
            existing.severity = alert.severity
            existing.cvss_score = alert.cvss_score
            existing.published_at = alert.published_at
        else:
            self.db.add(alert)

    async def _poll_cvefeed(self):
        """Parses RSS feeds from CVEFeed.io."""
        for url, sev in [
            (CVEFEED_CRITICAL_URL, CVESeverity.CRITICAL),
            (CVEFEED_HIGH_URL, CVESeverity.HIGH),
        ]:
            try:
                response = await self.client.get(url)
                feed = feedparser.parse(response.text)
                for entry in feed.entries:
                    cve_id = entry.title.split(":")[0].strip()
                    if not cve_id.startswith("CVE-"):
                        continue

                    # Extracting the date with fallback
                    if hasattr(entry, "published_parsed") and entry.published_parsed:
                        published_at = datetime(*entry.published_parsed[:6], tzinfo=UTC)
                    elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                        published_at = datetime(*entry.updated_parsed[:6], tzinfo=UTC)
                    else:
                        published_at = datetime.now(UTC)

                    alert = CVEAlert(
                        cve_id=cve_id,
                        title=entry.title,
                        description=entry.summary,
                        severity=sev,
                        cvss_score=9.0 if sev == CVESeverity.CRITICAL else 7.5,
                        category="General",
                        source_type=CVESourceType.CVEFEED,
                        url=entry.link,
                        published_at=published_at,
                    )
                    await self._upsert_cve(alert)
            except Exception as e:
                logger.error(f"Erreur CVEFeed {url}: {e}")

    async def close(self):
        await self.client.aclose()
