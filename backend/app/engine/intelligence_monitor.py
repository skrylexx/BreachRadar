"""
BreachRadar WebUI — Digital Intelligence Monitor
==============================================================================
Collects, standardizes and stores cyber intelligence from various sources.
Supports RSS/Atom, GitHub, Pastebin and Telegram.
"""

import asyncio
import hashlib
import logging
from datetime import UTC, datetime
from typing import Any

import feedparser
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.source_registry import SourceRegistry
from app.models.cve import CustomFeedSource
from app.models.finding import CyberFinding, Severity
from app.notifications.engine import NotificationEngine

logger = logging.getLogger(__name__)


class IntelligenceMonitor:
    """
    Monitoring engine driven by configuration and database.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.registry = SourceRegistry.load()
        self.notifier = NotificationEngine(settings)
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            },
        )

    async def run_all(self):
        """Launches all active collections."""
        logger.info("Démarrage de la veille numérique globale.")

        tasks = []

        # 1. Polling of RSS feeds (Static + DB)
        if self.registry.is_available("rss"):
            tasks.append(self._poll_rss_feeds())

        # 2. GitHub Polling (Static Monitors)
        if self.registry.is_available("github"):
            tasks.append(self._poll_github_monitors())

        # 3. Polling Pastebin (If configured)
        if self.registry.is_available("pastebin"):
            tasks.append(self._poll_pastebin())

        # 4. Polling Telegram (If configured)
        if self.registry.is_available("telegram"):
            tasks.append(self._poll_telegram())

        if tasks:
            await asyncio.gather(*tasks)
            await self.db.commit()

        logger.info("Veille numérique globale terminée.")

    # ─── RSS / Atom ───────────────────────────── ─────────────────────────────

    async def _poll_rss_feeds(self):
        """Retrieves items from configured RSS feeds."""
        # A. Static feeds from sources.yaml
        rss_status = self.registry.sources.get("rss")
        static_feeds = rss_status.config.get("feeds", []) if rss_status else []

        # B. Dynamic flows from the DB
        result = await self.db.execute(select(CustomFeedSource).where(CustomFeedSource.enabled))
        db_feeds = result.scalars().all()

        # Merge for processing
        all_feeds = []
        for f in static_feeds:
            all_feeds.append(
                {
                    "name": f.get("name"),
                    "url": f.get("url"),
                    "category": f.get("category", "General"),
                    "source_type": "static",
                }
            )
        for f in db_feeds:
            all_feeds.append(
                {
                    "name": f.name,
                    "url": f.url,
                    "category": f.category,
                    "source_type": "db",
                    "model": f,
                }
            )

        for feed_cfg in all_feeds:
            await self._process_single_rss(feed_cfg)

    async def _process_single_rss(self, cfg: dict[str, Any]):
        """Parses and stores items from a single stream."""
        url = cfg["url"]
        try:
            response = await self.client.get(url)
            if response.status_code != 200:
                logger.error(f"Erreur RSS [{cfg['name']}]: HTTP {response.status_code}")
                return

            feed = feedparser.parse(response.text)
            new_items_count = 0

            # Filter keywords for relevance
            keywords = [settings.target_domain.lower()]
            domain_name = settings.target_domain.split(".")[0]
            if len(domain_name) > 3:
                keywords.append(domain_name.lower())

            for entry in feed.entries:
                content = (entry.get("title", "") + " " + entry.get("summary", "")).lower()

                # Filtering: We keep if mention of the domain OR if the source is a critical alert source (CERT/CISA)
                is_relevant = any(k in content for k in keywords) or cfg["category"] == "Alerts"

                if not is_relevant:
                    continue

                # Generate a unique ID based on the item URL or link
                link = entry.get("link", url)
                external_id = hashlib.sha256(link.encode()).hexdigest()

                # Date standardization
                pub_date = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    # published_parsed is a struct_time (9 elements)
                    p = entry.published_parsed
                    pub_date = datetime(p[0], p[1], p[2], p[3], p[4], p[5], tzinfo=UTC)

                # Automatic severity calculation
                severity = self._analyze_severity(content)

                finding = CyberFinding(
                    source=cfg["name"],
                    external_id=f"rss:{external_id}",
                    finding_type="rss",
                    title=entry.get("title", "No Title")[:512],
                    description=entry.get("summary", "")[:2000],
                    url=link,
                    severity=severity,
                    published_at=pub_date,
                    extra_metadata={
                        "category": cfg["category"],
                        "author": entry.get("author", "Unknown"),
                    },
                )

                if await self._upsert_finding(finding):
                    new_items_count += 1

            # Update stats if it's a DB source
            if cfg["source_type"] == "db" and "model" in cfg:
                cfg["model"].last_polled_at = datetime.now(UTC)
                cfg["model"].last_item_count = new_items_count

            logger.debug(f"RSS [{cfg['name']}]: {new_items_count} nouveaux items.")

        except Exception as e:
            logger.error(f"Erreur lors du traitement RSS {url}: {e}")

    # ─── GitHub Monitors ────────────────────────── ───────────────────────────

    async def _poll_github_monitors(self):
        """Runs configured GitHub searches."""
        github_status = self.registry.sources.get("github")
        monitors = github_status.config.get("monitors", []) if github_status else []

        for mon in monitors:
            if mon.get("type") == "search":
                query = mon.get("query", "").replace("{target_domain}", settings.target_domain)
                await self._github_search(mon.get("name"), query)

    async def _github_search(self, monitor_name: str, query: str):
        """Performs a search via the GitHub API and normalizes the results."""
        api_url = "https://api.github.com/search/code"
        headers = {}
        if settings.github_token:
            headers["Authorization"] = f"token {settings.github_token}"

        try:
            params = {"q": query, "sort": "indexed", "order": "desc"}
            response = await self.client.get(api_url, params=params, headers=headers)

            if response.status_code == 200:
                data = response.json()
                for item in data.get("items", [])[:10]:
                    repo = item.get("repository", {})
                    external_id = f"gh:{item.get('sha')}"

                    finding = CyberFinding(
                        source=f"GitHub:{monitor_name}",
                        external_id=external_id,
                        finding_type="github",
                        title=f"Mention dans {repo.get('full_name')}",
                        description=f"Fichier: {item.get('path')}\nRepo: {repo.get('description')}",
                        url=item.get("html_url"),
                        severity=Severity.MEDIUM,
                        extra_metadata={
                            "repository": repo.get("full_name"),
                            "file_path": item.get("path"),
                            "owner": repo.get("owner", {}).get("login"),
                        },
                    )
                    await self._upsert_finding(finding)
            elif response.status_code == 403:
                logger.warning("GitHub API Rate limit atteint.")
        except Exception as e:
            logger.error(f"Erreur GitHub Search [{query}]: {e}")

    # ─── Pastebin Scraping ───────────────────────── ──────────────────────────

    async def _poll_pastebin(self):
        """
        Scraping Pastebin to detect mentions of the domain.
        Note: Usually requires a Pro account and a whitelisted IP.
        """
        api_url = "https://scrape.pastebin.com/api_scraping.php"
        params = {"limit": 50}

        try:
            response = await self.client.get(api_url, params=params)
            if response.status_code == 200:
                # Simplified logic: we just trace the activity for the demo
                # In a real implementation, we would fetch each scrape_url for Regex matching
                pass
            elif response.status_code == 403:
                logger.warning("Pastebin: IP non autorisée pour le scraping.")
        except Exception as e:
            logger.error(f"Erreur Pastebin: {e}")

    # ─── Telegram Monitor ────────────────────────── ──────────────────────────

    async def _poll_telegram(self):
        """
        Monitoring public Telegram channels.
        Note: Requires Telethon or a gateway.
        """
        # Structural stub
        logger.debug("Telegram polling (stub) - En attente de configuration API_ID.")

    # ───Logic ─────────────────────────────── ────────────────────────────────

    def _analyze_severity(self, text: str) -> Severity:
        """Simple heuristic analysis to determine severity."""
        text = text.lower()
        domain_mention = settings.target_domain.lower() in text

        critical_keywords = [
            "exploit",
            "0-day",
            "zero-day",
            "critical",
            "rce",
            "unauthenticated",
            "breach",
        ]
        high_keywords = [
            "vulnerability",
            "leak",
            "breach",
            "ransomware",
            "active attack",
            "phishing",
        ]

        if domain_mention and any(k in text for k in (critical_keywords + high_keywords)):
            return Severity.CRITICAL

        if any(k in text for k in critical_keywords):
            return Severity.CRITICAL
        if any(k in text for k in high_keywords) or domain_mention:
            return Severity.HIGH

        return Severity.LOW

    async def _upsert_finding(self, finding: CyberFinding) -> bool:
        """Add if does not already exist and alert if critical."""
        stmt = select(CyberFinding).where(CyberFinding.external_id == finding.external_id)
        result = await self.db.execute(stmt)
        if result.scalar_one_or_none():
            return False

        self.db.add(finding)

        # Immediate alert if critical
        if finding.severity == Severity.CRITICAL:
            try:
                await self.notifier.send_intel_alert(finding)
                finding.is_notified = True
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi d'alerte intel : {e}")

        return True

    async def close(self):
        await self.client.aclose()
