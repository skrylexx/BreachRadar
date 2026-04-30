"""
breachradar/main.py

Point d'entrée principal de l'application BreachRadar.
Fournit une interface CLI (Command Line Interface) basée sur Typer.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Optional

import typer
from rich.console import Console

from breachradar.clients.ransomlook import RansomLookClient
from breachradar.config.settings import get_settings
from breachradar.config.source_registry import SourceRegistry
from breachradar.core.aggregator import ResultAggregator
from breachradar.core.orchestrator import ScanOrchestrator
from breachradar.core.ransom_tracker import RansomwareTracker
from breachradar.core.scheduler import ScanScheduler
from breachradar.models.report import ReportMetadata
from breachradar.clients.github_webhook import start_webhook_server
from breachradar.notifications.engine import NotificationEngine
from breachradar.report.engine import ReportEngine
from breachradar.resolver.email_resolver import EmailResolver

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = typer.Typer(
    help="BreachRadar - Outil OSINT défensif pour la surveillance des fuites de données.",
    no_args_is_help=True,
)
console = Console()

settings = get_settings()
registry = SourceRegistry.load()


@app.command()
def sources(status: bool = typer.Option(False, "--status", help="Affiche l'état de toutes les sources")) -> None:
    """Gère et affiche les sources configurées."""
    if status:
        console.print(registry.format_status_table())
    else:
        active = registry.active_sources
        console.print(f"Sources actives ({len(active)}): {', '.join(active)}")


@app.command()
def ransomlook(check: bool = typer.Option(False, "--check", help="Vérifie immédiatement le domaine sur RansomLook")) -> None:
    """Commandes spécifiques à RansomLook."""
    if check:
        console.print(f"[bold blue]Lancement de la vérification RansomLook d'urgence pour {settings.target_domain}...[/bold blue]")
        
        async def run_ransomlook() -> None:
            client = RansomLookClient(base_url=settings.ransomlook_url, search_terms=settings.ransomlook_search_terms)
            notifier = NotificationEngine(settings=settings)
            tracker = RansomwareTracker(client=client, notifier=notifier)
            
            findings = await tracker.run(domain=settings.target_domain)
            if findings:
                console.print(f"[bold red]ALERTE : {len(findings)} mention(s) trouvée(s) sur des portails ransomware ![/bold red]")
                for f in findings:
                    console.print(f"- {f.group_display_name}: {f.victim_name} (Sévérité: {f.severity})")
            else:
                console.print("[bold green]✅ Aucun résultat trouvé sur les portails ransomware.[/bold green]")
                
        asyncio.run(run_ransomlook())


@app.command()
def check(email: str = typer.Option(..., "--email", help="Adresse email spécifique à vérifier")) -> None:
    """Vérifie une adresse email spécifique."""
    console.print(f"[bold blue]Vérification de l'email {email}...[/bold blue]")
    
    async def run_check() -> None:
        orchestrator = ScanOrchestrator(settings=settings, registry=registry)
        findings = await orchestrator.scan_emails([email])
        
        if findings:
            console.print(f"[bold yellow]⚠️ {len(findings)} fuite(s) détectée(s) pour {email}[/bold yellow]")
            for f in findings:
                console.print(f"- {f.breach_date} | {f.breach_name} | {f.source}")
        else:
            console.print(f"[bold green]✅ Aucune fuite détectée pour {email}[/bold green]")
            
    asyncio.run(run_check())


@app.command()
def scan(
    format: Optional[str] = typer.Option(None, "--format", help="Formats de rapport séparés par des virgules (ex: markdown,json)"),
) -> None:
    """Lance un scan complet du domaine."""
    formats = format.split(",") if format else settings.report_format
    console.print(f"[bold blue]Démarrage du scan complet pour le domaine: {settings.target_domain}[/bold blue]")
    
async def _execute_full_scan(formats: list[str]) -> None:
    start_time = datetime.utcnow()
    
    # 1. Tracker RansomLook (Priorité absolue)
    rl_client = RansomLookClient(base_url=settings.ransomlook_url, search_terms=settings.ransomlook_search_terms)
    notifier = NotificationEngine(settings=settings)
    tracker = RansomwareTracker(client=rl_client, notifier=notifier)
    
    console.print("[cyan]Étape 1: Surveillance Ransomware...[/cyan]")
    ransom_findings = await tracker.run(domain=settings.target_domain)
    
    # 2. Résolution des emails
    console.print("[cyan]Étape 2: Résolution des emails...[/cyan]")
    resolver = EmailResolver(domain=settings.target_domain)
    emails = await resolver.resolve()
    
    # 3. Orchestration des scans par sources
    console.print(f"[cyan]Étape 3: Scan de {len(emails)} email(s) et du domaine sur les sources actives...[/cyan]")
    orchestrator = ScanOrchestrator(settings=settings, registry=registry)
    
    email_findings = await orchestrator.scan_emails(emails)
    domain_findings = await orchestrator.scan_domain(settings.target_domain)
    
    # Combiner les findings (sans doublons stricts)
    all_findings = email_findings + domain_findings
    
    # 4. Agrégation et Rapport
    console.print("[cyan]Étape 4: Agrégation et génération du rapport...[/cyan]")
    
    end_time = datetime.utcnow()
    duration = (end_time - start_time).total_seconds()
    
    metadata = ReportMetadata(
        target_domain=settings.target_domain,
        sources_queried=registry.active_sources,
        scan_duration_seconds=duration,
        total_emails_checked=len(emails),
        total_findings=len(all_findings),
    )
    
    # Ajouter le contexte RansomLook
    rl_stats = await tracker.get_context()
    metadata.ransomlook_instance = {
        "url": rl_stats.instance_url,
        "is_healthy": rl_stats.is_healthy,
        "groups_tracked": rl_stats.groups_tracked,
        "total_posts_indexed": rl_stats.total_posts,
        "last_update": rl_stats.last_update,
    }
    
    aggregator = ResultAggregator()
    final_report = aggregator.aggregate(
        email_findings=all_findings,
        ransom_findings=ransom_findings,
        metadata=metadata,
    )
    final_report.ransomlook_stats = rl_stats
    
    report_engine = ReportEngine(output_dir=settings.report_output_dir)
    files = report_engine.generate(report=final_report, formats=formats)
    
    console.print("\n[bold green]✅ Scan terminé ![/bold green]")
    console.print(f"Sévérité globale: {final_report.get_global_severity_label()}")
    console.print("Fichiers générés :")
    for f in files:
        console.print(f"- {f}")

@app.command()
def scan(
    format: Optional[str] = typer.Option(None, "--format", help="Formats de rapport séparés par des virgules (ex: markdown,json)"),
) -> None:
    """Lance un scan complet du domaine."""
    formats = format.split(",") if format else settings.report_format
    console.print(f"[bold blue]Démarrage du scan complet pour le domaine: {settings.target_domain}[/bold blue]")
    
    asyncio.run(_execute_full_scan(formats))


@app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def schedule(ctx: typer.Context) -> None:
    """Démarre le planificateur (Scheduler) pour des scans récurrents."""
    console.print(f"[bold blue]Lancement du planificateur pour {settings.target_domain}...[/bold blue]")
    
    # Forçage de l'activation si lancé manuellement via CLI
    if not settings.schedule_enabled:
        console.print("[bold yellow]Attention: schedule_enabled est False dans .env. Forçage à True pour cette exécution.[/bold yellow]")
        settings.schedule_enabled = True

    async def _scan_callback():
        await _execute_full_scan(settings.report_format)

    scheduler = ScanScheduler(settings=settings, scan_callback=_scan_callback)
    scheduler.start()
    
    loop = asyncio.get_event_loop()
    
    # Démarrer le serveur Webhook GitHub si configuré sur un port > 0
    # On va le démarrer par défaut sur le port 8080 si ce n'est pas désactivé
    # (Ou on peut ajouter une option github_webhook_port dans settings)
    webhook_port = getattr(settings, 'github_webhook_port', 8080)
    if webhook_port > 0:
        loop.create_task(start_webhook_server(port=webhook_port))

    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        console.print("[bold yellow]Arrêt du planificateur.[/bold yellow]")


if __name__ == "__main__":
    app()
