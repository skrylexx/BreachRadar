"""
leakmonitor/core/scheduler.py

Planificateur de tâches (Scheduler).
La planification avancée (via APScheduler) est prévue pour la Phase 2.
"""

from __future__ import annotations

import logging
import asyncio
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from leakmonitor.config.settings import Settings

logger = logging.getLogger(__name__)

class ScanScheduler:
    """
    Planificateur de tâches utilisant APScheduler.
    """
    def __init__(self, settings: Settings, scan_callback) -> None:
        self.settings = settings
        self.scheduler = AsyncIOScheduler()
        self.scan_callback = scan_callback

    def start(self) -> None:
        if not self.settings.schedule_enabled:
            logger.info("Le planificateur est désactivé dans la configuration.")
            return

        try:
            trigger = CronTrigger.from_crontab(self.settings.schedule_cron)
            self.scheduler.add_job(
                self._run_scan_job,
                trigger=trigger,
                id="main_scan_job",
                name="Scan Complet Périodique",
                replace_existing=True
            )
            self.scheduler.start()
            logger.info(f"Planificateur démarré avec le cron : '{self.settings.schedule_cron}'")
        except ValueError as e:
            logger.error(f"Expression cron invalide : {self.settings.schedule_cron} - {e}")

    async def _run_scan_job(self) -> None:
        logger.info(f"[{datetime.utcnow().isoformat()}] Démarrage automatique du scan via Scheduler...")
        try:
            await self.scan_callback()
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution du scan planifié : {e}")
