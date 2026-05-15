"""
BreachRadar WebUI — Routeur Reports
====================================
Gestion des rapports de sécurité (liste, génération globale, export PDF).
"""

import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.dependencies.auth import AdminUser, ViewerUser
from app.models.scan import ScanResult, ScanStatus, ScanSeverity
from app.models.audit_log import AuditLog
from app.schemas.common import PaginatedResponse
from app.report.engine import ReportEngine

router = APIRouter()

# ─── Schémas ──────────────────────────────────────────────────────────────────

from pydantic import BaseModel

class ReportRead(BaseModel):
    id: str
    generated_at: datetime
    domain: str
    severity: str
    emails_compromised: int
    has_ransomware_alert: bool
    type: str
    finding_counts: dict

    model_config = {"from_attributes": True}

class ReportGenerateRequest(BaseModel):
    start_date: datetime
    end_date: datetime

# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.get("", response_model=PaginatedResponse[ReportRead])
async def list_reports(
    current_user: ViewerUser,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(25, ge=1, le=100),
    offset: int = Query(0, ge=0),
    period: Optional[str] = Query(None, pattern="^(7d|1m|30d|6m|12m)$"),
) -> PaginatedResponse[ReportRead]:
    """Liste les rapports générés (basé sur les ScanResult terminés)."""
    stmt = select(ScanResult).where(ScanResult.status == ScanStatus.COMPLETED).order_by(desc(ScanResult.completed_at))
    
    if period:
        days = {"7d": 7, "1m": 30, "30d": 30, "6m": 180, "12m": 365}[period]
        since = datetime.now(timezone.utc) - timedelta(days=days)
        stmt = stmt.where(ScanResult.completed_at >= since)
        
    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = (await db.execute(count_stmt)).scalar() or 0
    
    # Get items
    result = await db.execute(stmt.offset(offset).limit(limit))
    scans = result.scalars().all()
    
    items = []
    for s in scans:
        # Transformation de ScanResult en ReportRead
        items.append(ReportRead(
            id=str(s.id),
            generated_at=s.completed_at or s.started_at,
            domain=s.target_domain,
            severity=s.severity.value.upper() if s.severity else "NONE",
            emails_compromised=s.breach_findings,
            has_ransomware_alert=s.ransomware_findings > 0,
            type="manual" if s.triggered_by.startswith("manual") else "scheduled",
            finding_counts=s.findings_by_source or {} # Simplifié pour le Record<Severity, number>
        ))
        
    return PaginatedResponse(
        items=items,
        total=total,
        page=(offset // limit) + 1,
        page_size=limit
    )

@router.get("/{report_id}/export")
async def export_report(
    report_id: str,
    format: str = Query("pdf", pattern="^(pdf|json|html)$"),
    current_user: ViewerUser = Depends(ViewerUser),
    db: AsyncSession = Depends(get_db)
):
    """Exporte un rapport existant dans le format demandé."""
    result = await db.execute(select(ScanResult).where(ScanResult.id == uuid.UUID(report_id)))
    scan = result.scalar_one_or_none()
    
    if not scan or not scan.report_path:
        raise HTTPException(status_code=404, detail="Report not found or not yet generated")

    base_path = Path(scan.report_path)
    if not base_path.exists():
        # Tenter de retrouver le fichier si le chemin a changé (ex: docker restart)
        filename = base_path.name
        base_path = Path(settings.report_output_dir) / filename
        if not base_path.exists():
            raise HTTPException(status_code=404, detail="Report file missing on disk")

    # Si on veut du JSON ou HTML, on renvoie directement le fichier existant
    if format == "json":
        json_path = base_path.with_suffix(".json")
        if json_path.exists():
            return FileResponse(json_path, media_type="application/json", filename=json_path.name)
    elif format == "html":
        html_path = base_path.with_suffix(".html")
        if html_path.exists():
            return FileResponse(html_path, media_type="text/html", filename=html_path.name)
    
    # Si on veut du PDF, on vérifie s'il existe déjà ou on le génère
    pdf_path = base_path.with_suffix(".pdf")
    if pdf_path.exists():
        return FileResponse(pdf_path, media_type="application/pdf", filename=pdf_path.name)
    
    # Génération à la volée si nécessaire
    # Note: On a besoin du FinalReport complet pour re-générer. 
    # Pour l'instant, on suppose que le scan a déjà généré les fichiers de base.
    # On va lire le JSON pour reconstruire le FinalReport et appeler _generate_pdf.
    
    json_file = base_path.with_suffix(".json")
    if not json_file.exists():
        raise HTTPException(status_code=404, detail="Original report data (JSON) missing")
    
    from app.models.report import FinalReport
    import json
    with open(json_file, "r", encoding="utf-8") as f:
        report_data = json.load(f)
        report = FinalReport.model_validate(report_data)
        
    engine = ReportEngine(output_dir=settings.report_output_dir)
    pdf_file = engine._generate_pdf(report, pdf_path.name)
    
    return FileResponse(pdf_file, media_type="application/pdf", filename=pdf_file.name)

@router.post("/generate")
async def generate_global_report(
    body: ReportGenerateRequest,
    current_user: AdminUser,
    db: AsyncSession = Depends(get_db)
):
    """
    Génère un rapport consolidé sur une période donnée.
    Récupère tous les findings des scans effectués entre start_date et end_date.
    """
    import json
    from app.models.report import FinalReport, ReportMetadata
    from app.engine.aggregator import ResultAggregator
    from app.report.engine import ReportEngine

    # 1. Récupérer les ScanResult de la période
    stmt = (
        select(ScanResult)
        .where(ScanResult.status == ScanStatus.COMPLETED)
        .where(ScanResult.completed_at >= body.start_date)
        .where(ScanResult.completed_at <= body.end_date)
    )
    result = await db.execute(stmt)
    scans = result.scalars().all()
    
    if not scans:
        raise HTTPException(status_code=404, detail="No scans found in this period")

    # 2. Agréger les données de tous les scans
    all_leak_findings = []
    all_ransom_findings = []
    sources_queried = set()
    
    for scan in scans:
        if not scan.report_path:
            continue
            
        json_path = Path(scan.report_path).with_suffix(".json")
        if not json_path.exists():
            continue
            
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                report_data = json.load(f)
                report_obj = FinalReport.model_validate(report_data)
                
                # Extraire les findings individuels (LeakFinding)
                for email_res in report_obj.findings:
                    all_leak_findings.extend(email_res.findings)
                
                # Extraire les alertes ransomware
                all_ransom_findings.extend(report_obj.ransomware_alerts.alerts)
                
                # Fusionner les sources
                sources_queried.update(report_obj.report_metadata.sources_queried)
        except Exception as e:
            print(f"Error loading report {json_path}: {e}")

    # 3. Créer le nouveau rapport consolidé
    aggregator = ResultAggregator()
    metadata = ReportMetadata(
        target_domain=settings.target_domain,
        generated_at=datetime.now(timezone.utc),
        scan_duration_seconds=0.0,
        sources_queried=list(sources_queried),
        total_emails_checked=0, # Difficile à recalculer sans les logs de scan
        total_findings=len(all_leak_findings) + len(all_ransom_findings)
    )
    
    consolidated_report = aggregator.aggregate(
        email_findings=all_leak_findings,
        ransom_findings=all_ransom_findings,
        metadata=metadata
    )

    # 4. Générer les fichiers
    engine = ReportEngine(output_dir=settings.report_output_dir)
    # On ajoute "global_" au début du nom de fichier via le timestamp
    timestamp = datetime.now(timezone.utc).strftime("GLOBAL_%Y%m%d_%H%M%S")
    report_files = engine.generate(consolidated_report, formats=["json", "html", "pdf"])

    # 5. Logger l'action
    db.add(AuditLog(
        user_email=current_user.email,
        action="report.global_generated",
        details={
            "start_date": body.start_date.isoformat(), 
            "end_date": body.end_date.isoformat(), 
            "scans_included": len(scans),
            "output_path": str(report_files[0]) if report_files else None
        },
        ip_address=None
    ))
    
    return {
        "status": "ok", 
        "message": f"Global report based on {len(scans)} scans has been generated.",
        "report_id": str(scans[0].id), # On renvoie un ID pour que l'UI puisse le lister ou on devrait créer un ScanResult type "GLOBAL"
        "scans_included": len(scans)
    }
