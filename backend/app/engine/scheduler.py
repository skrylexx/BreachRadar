"""
breachradar/core/scheduler.py

Planificateur de tâches (Scheduler).
La planification avancée (via APScheduler) est prévue pour la Phase 2.
"""

from __future__ import annotations

import logging
import asyncio
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import Settings

logger = logging.getLogger(__name__)

class ScanScheduler:
    """
    Planificateur de tâches utilisant APScheduler.
    """
    def __init__(self, settings: Settings, scan_callback, cve_callback=None) -> None:
        self.settings = settings
        self.scheduler = AsyncIOScheduler()
        self.scan_callback = scan_callback
        self.cve_callback = cve_callback

    def start(self) -> None:
        if not self.settings.schedule_enabled:
            logger.info("Le planificateur est désactivé dans la configuration.")
            return

        # 1. Job de Scan Complet
        try:
            trigger = CronTrigger.from_crontab(self.settings.schedule_cron)
            self.scheduler.add_job(
                self._run_scan_job,
                trigger=trigger,
                id="main_scan_job",
                name="Scan Complet Périodique",
                replace_existing=True
            )
            logger.info(f"Job de scan planifié avec le cron : '{self.settings.schedule_cron}'")
        except ValueError as e:
            logger.error(f"Expression cron invalide pour le scan : {self.settings.schedule_cron} - {e}")

        # 2. Job de Veille CVE (si callback fourni)
        if self.cve_callback:
            # Interval par défaut : 1 heure si non spécifié
            interval_minutes = getattr(self.settings, "cve_polling_interval", 60)
            self.scheduler.add_job(
                self._run_cve_job,
                "interval",
                minutes=interval_minutes,
                id="cve_polling_job",
                name="Veille CVE Périodique",
                replace_existing=True
            )
            logger.info(f"Job de veille CVE planifié toutes les {interval_minutes} minutes.")

        self.scheduler.start()
        logger.info("Planificateur APScheduler démarré.")

    async def _run_scan_job(self) -> None:
        logger.info(f"[{datetime.now().isoformat()}] Démarrage automatique du scan via Scheduler...")
        try:
            await self.scan_callback()
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution du scan planifié : {e}")

    async def _run_cve_job(self) -> None:
        logger.info(f"[{datetime.now().isoformat()}] Démarrage de la veille CVE via Scheduler...")
        try:
            await self.cve_callback()
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de la veille CVE : {e}")
