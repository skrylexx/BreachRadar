"""
leakmonitor/core/scheduler.py

Planificateur de tâches (Scheduler).
La planification avancée (via APScheduler) est prévue pour la Phase 2.
"""

from __future__ import annotations

import logging

from leakmonitor.config.settings import Settings

logger = logging.getLogger(__name__)

class ScanScheduler:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        
    def start(self) -> None:
        logger.info("Le planificateur (Scheduler) sera implémenté en Phase 2.")
        pass
