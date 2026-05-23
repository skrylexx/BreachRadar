"""
BreachRadar WebUI — Moteur de Veille Numérique (Intelligence Monitor)
=====================================================================
Collecte, normalise et stocke les renseignements cyber depuis des sources variées.
Supporte RSS/Atom, GitHub, et les sources personnalisées.
"""

import asyncio
import logging
import re
import uuid
import hashlib
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

import httpx
import feedparser
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.source_registry import SourceRegistry
from app.models.finding import CyberFinding, Severity
from app.models.cve import CustomFeedSource

logger = logging.getLogger(__name__)

class IntelligenceMonitor:
    """
    Moteur de veille piloté par la configuration et la base de données.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.registry = SourceRegistry.load()
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={"User-Agent": f"BreachRadar/1.0 (Watch-Engine; {settings.target_domain})"}
        )

    async def run_all(self):
        """Lance toutes les collectes actives."""
        logger.info("Démarrage de la veille numérique globale.")
        
        tasks = []
        
        # 1. Polling des flux RSS (Statiques + DB)
        if self.registry.is_available("rss"):
            tasks.append(self._poll_rss_feeds())
            
        # 2. Polling GitHub (Monitors statiques)
        if self.registry.is_available("github"):
            tasks.append(self._poll_github_monitors())

        if tasks:
            await asyncio.gather(*tasks)
            await self.db.commit()
            
        logger.info("Veille numérique globale terminée.")

    # ─── RSS / Atom ──────────────────────────────────────────────────────────

    async def _poll_rss_feeds(self):
        """Récupère les items depuis les flux RSS configurés."""
        # A. Flux statiques depuis sources.yaml
        rss_status = self.registry.sources.get("rss")
        static_feeds = rss_status.config.get("feeds", []) if rss_status else []
        
        # B. Flux dynamiques depuis la DB
        result = await self.db.execute(select(CustomFeedSource).where(CustomFeedSource.enabled == True))
        db_feeds = result.scalars().all()
        
        # Fusionner pour le traitement
        all_feeds = []
        for f in static_feeds:
            all_feeds.append({
                "name": f.get("name"),
                "url": f.get("url"),
                "category": f.get("category", "General"),
                "source_type": "static"
            })
        for f in db_feeds:
            all_feeds.append({
                "name": f.name,
                "url": f.url,
                "category": f.category,
                "source_type": "db",
                "model": f
            })

        for feed_cfg in all_feeds:
            await self._process_single_rss(feed_cfg)

    async def _process_single_rss(self, cfg: Dict[str, Any]):
        """Parse et stocke les items d'un flux unique."""
        url = cfg["url"]
        try:
            response = await self.client.get(url, follow_redirects=True)
            if response.status_code != 200:
                logger.error(f"Erreur RSS [{cfg['name']}]: HTTP {response.status_code}")
                return

            feed = feedparser.parse(response.text)
            new_items_count = 0
            
            # Mots-clés de filtrage pour pertinence
            keywords = [settings.target_domain.lower()]
            # On ajoute des variantes si le domaine est complexe
            domain_name = settings.target_domain.split('.')[0]
            if len(domain_name) > 3:
                keywords.append(domain_name.lower())

            for entry in feed.entries:
                content = (entry.get("title", "") + " " + entry.get("summary", "")).lower()
                
                # Filtrage : On garde si mention du domaine OU si la source est une source d'alerte critique (CERT/CISA)
                is_relevant = any(k in content for k in keywords) or cfg["category"] == "Alerts"
                
                if not is_relevant:
                    continue

                # Générer un ID unique basé sur l'URL de l'item ou le lien
                link = entry.get("link", url)
                external_id = hashlib.sha256(link.encode()).hexdigest()
                
                # Normalisation de la date
                pub_date = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    pub_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)

                # Calcul automatique de la sévérité (basé sur mots-clés pour le moment)
                severity = self._analyze_severity(entry.get("title", "") + " " + entry.get("summary", ""))

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
                        "author": entry.get("author", "Unknown")
                    }
                )
                
                if await self._upsert_finding(finding):
                    new_items_count += 1

            # Mettre à jour les stats si c'est une source DB
            if cfg["source_type"] == "db" and "model" in cfg:
                cfg["model"].last_polled_at = datetime.now(timezone.utc)
                cfg["model"].last_item_count = new_items_count
                
            logger.debug(f"RSS [{cfg['name']}]: {new_items_count} nouveaux items.")
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement RSS {url}: {e}")

    # ─── GitHub Monitors ─────────────────────────────────────────────────────

    async def _poll_github_monitors(self):
        """Exécute les recherches GitHub configurées."""
        github_status = self.registry.sources.get("github")
        monitors = github_status.config.get("monitors", []) if github_status else []
        
        for mon in monitors:
            if mon.get("type") == "search":
                query = mon.get("query", "").replace("{target_domain}", settings.target_domain)
                await self._github_search(mon.get("name"), query)

    async def _github_search(self, monitor_name: str, query: str):
        """Effectue une recherche via l'API GitHub et normalise les résultats."""
        api_url = "https://api.github.com/search/code"
        headers = {}
        if settings.github_token:
            headers["Authorization"] = f"token {settings.github_token}"
        
        try:
            params = {"q": query, "sort": "indexed", "order": "desc"}
            response = await self.client.get(api_url, params=params, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                for item in data.get("items", [])[:10]: # Limite aux 10 plus récents
                    repo = item.get("repository", {})
                    external_id = f"gh:{item.get('sha')}"
                    
                    finding = CyberFinding(
                        source=f"GitHub:{monitor_name}",
                        external_id=external_id,
                        finding_type="github",
                        title=f"Mention dans {repo.get('full_name')}",
                        description=f"Fichier: {item.get('path')}\nRepo: {repo.get('description')}",
                        url=item.get("html_url"),
                        severity=Severity.MEDIUM, # GitHub mention est souvent suspect
                        extra_metadata={
                            "repository": repo.get("full_name"),
                            "file_path": item.get("path"),
                            "owner": repo.get("owner", {}).get("login")
                        }
                    )
                    await self._upsert_finding(finding)
            elif response.status_code == 403:
                logger.warning("GitHub API Rate limit atteint.")
        except Exception as e:
            logger.error(f"Erreur GitHub Search [{query}]: {e}")

    # ─── Logic ───────────────────────────────────────────────────────────────

    def _analyze_severity(self, text: str) -> Severity:
        """Analyse heuristique simple pour déterminer la sévérité."""
        text = text.lower()
        
        # Mots-clés prioritaires (Domaine mentionné directement)
        domain_mention = settings.target_domain.lower() in text
        
        critical_keywords = ["exploit", "0-day", "zero-day", "critical", "rce", "unauthenticated", "breach"]
        high_keywords = ["vulnerability", "leak", "breach", "ransomware", "active attack", "phishing"]
        
        if domain_mention and any(k in text for k in (critical_keywords + high_keywords)):
            return Severity.CRITICAL
            
        if any(k in text for k in critical_keywords):
            return Severity.CRITICAL
        if any(k in text for k in high_keywords) or domain_mention:
            return Severity.HIGH
        
        return Severity.LOW

    async def _upsert_finding(self, finding: CyberFinding) -> bool:
        """Ajoute si n'existe pas déjà (basé sur external_id)."""
        stmt = select(CyberFinding).where(CyberFinding.external_id == finding.external_id)
        result = await self.db.execute(stmt)
        if result.scalar_one_or_none():
            return False
        
        self.db.add(finding)
        return True

    async def close(self):
        await self.client.aclose()
