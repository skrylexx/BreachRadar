"""
BreachRadar WebUI — Logic
==========================
Orchestration de haut niveau pour l'exécution complète d'un scan.
Fait le lien entre les différents modules (Orchestrator, Tracker, Aggregator, Report, Notifications).
"""

import asyncio
import logging
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import update

from app.clients.ransomlook import RansomLookClient
from app.core.config import settings
from app.core.source_registry import SourceRegistry
from app.engine.aggregator import ResultAggregator
from app.engine.orchestrator import ScanOrchestrator
from app.engine.ransom_tracker import RansomwareTracker
from app.models.report import ReportMetadata
from app.models.scan import ScanResult, ScanSeverity, ScanStatus
from app.notifications.engine import NotificationEngine
from app.report.engine import ReportEngine
from app.resolver.email_resolver import EmailResolver

logger = logging.getLogger(__name__)


class ScanManager:
    """
    Gère le cycle de vie complet d'un scan.
    """

    def __init__(self) -> None:
        self.registry = SourceRegistry.load()
        self.notifier = NotificationEngine(settings=settings)
        self.aggregator = ResultAggregator()
        self.report_engine = ReportEngine(output_dir=settings.report_output_dir)

    async def _get_api_keys(self, db) -> dict[str, str]:
        """Charge toutes les clés API actives depuis la base de données."""
        from sqlalchemy import select

        from app.core.security import decrypt_secret
        from app.models.api_key import APIKey

        result = await db.execute(select(APIKey).where(APIKey.is_active))
        keys = {}
        for k in result.scalars().all():
            try:
                keys[k.service_name] = decrypt_secret(k.encrypted_key)
            except Exception as e:
                logger.error(f"Erreur déchiffrement clé {k.service_name}: {e}")
                continue
        return keys

    async def run_full_scan(self, scan_id: UUID, target_domain: str | None = None) -> None:
        """
        Exécute le scan complet en arrière-plan.
        Gère sa propre session DB pour éviter les problèmes de session fermée par le routeur.
        """
        from app.core.database import AsyncSessionLocal

        domain = target_domain or settings.target_domain
        logger.info(f"Démarrage du scan complet pour le domaine : {domain} (ID: {scan_id})")

        async with AsyncSessionLocal() as db:
            try:
                # 0. Charger les clés API de la base
                db_keys = await self._get_api_keys(db)

                # 1. Initialiser les clients avec les clés fraîches
                orchestrator = ScanOrchestrator(
                    settings=settings, registry=self.registry, api_keys=db_keys
                )

                # Client RansomLook (priorité SaaS key DB)
                mode = settings.ransomlook_mode
                api_key = db_keys.get("ransomlook_saas")

                ransom_client = RansomLookClient(mode=mode, api_key=api_key)
                tracker = RansomwareTracker(client=ransom_client, notifier=self.notifier)

                # 2. Résolution des adresses email
                resolver = EmailResolver(domain=domain)
                emails = await resolver.resolve()

                # 3. Exécution des scans en parallèle
                ransom_task = asyncio.create_task(tracker.run(domain))
                leak_task = asyncio.create_task(orchestrator.scan_emails(emails))
                domain_leak_task = asyncio.create_task(orchestrator.scan_domain(domain))

                # Attendre les résultats
                ransom_findings = await ransom_task
                leak_findings = await leak_task
                domain_findings = await domain_leak_task

                all_leak_findings = leak_findings + domain_findings

                # 4. Agrégation des résultats
                metadata = ReportMetadata(
                    target_domain=domain,
                    generated_at=datetime.now(UTC),
                    scan_duration_seconds=0.0,
                    sources_queried=self.registry.active_sources,
                    total_emails_checked=len(emails),
                    total_findings=len(all_leak_findings) + len(ransom_findings),
                )

                report = self.aggregator.aggregate(
                    email_findings=all_leak_findings,
                    ransom_findings=ransom_findings,
                    metadata=metadata,
                )

                # 4. Génération du rapport physique (JSON, HTML, PDF)
                report_files = self.report_engine.generate(report, formats=["json", "html", "pdf"])

                # 5. Mise à jour de la base de données
                severity_map = {
                    "CRITICAL": ScanSeverity.CRITICAL,
                    "HIGH": ScanSeverity.HIGH,
                    "MEDIUM": ScanSeverity.MEDIUM,
                    "LOW": ScanSeverity.LOW,
                }

                global_sev_str = (
                    report.summary.global_severity.value
                    if report.summary.global_severity
                    else "LOW"
                )
                scan_severity = severity_map.get(global_sev_str, ScanSeverity.LOW)

                await db.execute(
                    update(ScanResult)
                    .where(ScanResult.id == scan_id)
                    .values(
                        status=ScanStatus.COMPLETED,
                        severity=scan_severity,
                        total_findings=len(all_leak_findings) + len(ransom_findings),
                        report_path=str(report_files[0]) if report_files else None,
                        completed_at=datetime.now(UTC),
                    )
                )
                await db.commit()

                logger.info(f"Scan {scan_id} terminé avec succès. Sévérité: {scan_severity}")

            except Exception as e:
                logger.error(f"Échec critique du scan {scan_id} : {e}", exc_info=True)
                await db.execute(
                    update(ScanResult)
                    .where(ScanResult.id == scan_id)
                    .values(status=ScanStatus.FAILED, completed_at=datetime.now(UTC))
                )
                await db.commit()
