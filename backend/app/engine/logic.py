"""
BreachRadar WebUI — Logic
==========================
High-level orchestration for the complete execution of a scan.
Makes the link between the different modules (Orchestrator, Tracker, Aggregator, Report, Notifications).
"""

import asyncio
import logging
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select, update

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
    Manages the complete lifecycle of a scan.
    """

    def __init__(self) -> None:
        self.registry = SourceRegistry.load()
        self.notifier = NotificationEngine(settings=settings)
        self.aggregator = ResultAggregator()
        self.report_engine = ReportEngine(output_dir=settings.report_output_dir)

    async def _get_api_keys(self, db) -> dict[str, str]:
        """Loads all active API keys from the database."""
        from sqlalchemy import select

        from app.core.security import decrypt_secret
        from app.models.api_key import APIKey

        result = await db.execute(select(APIKey).where(APIKey.is_active))
        keys = {}
        for k in result.scalars().all():
            try:
                keys[k.service_name] = decrypt_secret(k.encrypted_key)
            except Exception as e:
                logger.error(f"Error decrypting key {k.service_name}: {e}")
                continue
        return keys

    async def run_full_scan(self, scan_id: UUID, target_domain: str | None = None) -> None:
        """
        Runs the full scan in the background.
        Manages its own DB session to avoid session closed by router issues.
        """
        from app.core.database import AsyncSessionLocal

        domain = target_domain or settings.target_domain
        logger.info(f"Starting full scan for domain: {domain} (ID: {scan_id})")

        async with AsyncSessionLocal() as db:
            try:
                # 0. Load the database API keys
                db_keys = await self._get_api_keys(db)

                # 1. Initialize clients with fresh keys
                orchestrator = ScanOrchestrator(settings=settings, registry=self.registry, api_keys=db_keys)

                # RansomLook client (SaaS key DB priority)
                mode = settings.ransomlook_mode
                api_key = db_keys.get("ransomlook_saas")

                ransom_client = RansomLookClient(mode=mode, api_key=api_key)
                tracker = RansomwareTracker(client=ransom_client, notifier=self.notifier)

                # 2. Email address resolution
                resolver = EmailResolver(domain=domain)
                emails = await resolver.resolve()

                # 3. Running scans in parallel
                ransom_task = asyncio.create_task(tracker.run(domain))
                leak_task = asyncio.create_task(orchestrator.scan_emails(emails))
                domain_leak_task = asyncio.create_task(orchestrator.scan_domain(domain))

                # Wait for the results
                ransom_findings = await ransom_task
                leak_findings = await leak_task
                domain_findings = await domain_leak_task

                all_leak_findings = leak_findings + domain_findings

                # 4. Aggregation of results
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

                # 4bis. Persistence of positive Ransomware detections in DB (CyberFinding)
                from app.models.finding import CyberFinding, Severity
                for f in ransom_findings:
                    external_id = f"ransom:{f.group_name}:{f.victim_name}"
                    # Check if already present via external_id
                    res_existing = await db.execute(select(CyberFinding).where(CyberFinding.external_id == external_id))
                    if not res_existing.scalar_one_or_none():
                        new_finding = CyberFinding(
                            source=f.group_display_name,
                            external_id=external_id,
                            finding_type="ransomware",
                            title=f"Victim detected: {f.victim_name}",
                            description=f.description or f"Publication detected on {f.group_display_name} portal",
                            url=f.portal_url,
                            severity=Severity.CRITICAL,
                            extra_metadata={
                                "group_name": f.group_name,
                                "victim_website": f.victim_website,
                                "claim_size": f.claim_size,
                                "status": f.status.value,
                                "search_term": f.search_term_matched
                            },
                            published_at=f.published_at,
                            discovered_at=f.discovered_at
                        )
                        db.add(new_finding)

                # 4. Generation of the physical report (JSON, HTML, PDF)
                report_files = self.report_engine.generate(report, formats=["json", "html", "pdf"])

                # 5. Database update
                severity_map = {
                    "CRITICAL": ScanSeverity.CRITICAL,
                    "HIGH": ScanSeverity.HIGH,
                    "MEDIUM": ScanSeverity.MEDIUM,
                    "LOW": ScanSeverity.LOW,
                }

                global_sev_str = report.summary.global_severity.value if report.summary.global_severity else "LOW"
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

                logger.info(f"Scan {scan_id} completed successfully. Severity: {scan_severity}")

            except Exception as e:
                logger.error(f"Critical scan failure {scan_id}: {e}", exc_info=True)
                await db.execute(
                    update(ScanResult)
                    .where(ScanResult.id == scan_id)
                    .values(status=ScanStatus.FAILED, completed_at=datetime.now(UTC))
                )
                await db.commit()
