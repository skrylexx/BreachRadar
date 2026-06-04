"""
breachradar/models/ransom.py

RansomLook specific Pydantic templates.

IMPORTANT SAFETY NOTE:
RansomLook data is PUBLIC in nature — it is published
deliberately by ransomware groups on their extortion portals.
This data does NOT require sanitization (unlike data
email/password from other sources).

However, the ransomware portal's .onion URL is NOT included in the
final reports (stored but hidden), to avoid easy access
directly to these portals.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class RansomStatus(StrEnum):
    """
    Status of the victim's publication on the ransomware portal.
    Based on public metadata available via RansomLook.
    """

    LISTED = "LISTED"  # Victim listed, data not yet published
    PUBLISHED = "PUBLISHED"  # Published/downloadable data
    REMOVED = "REMOVED"  # Post deleted (ransom paid?)
    UNKNOWN = "UNKNOWN"


class RansomFinding(BaseModel):
    """
    Result of a RansomLook match.

    ⚠️ MAXIMUM LEVEL ALERT: a RansomFinding indicates that a
    Massive exfiltration is likely or underway. The severity is
    ALWAYS CRITICAL — no negotiation possible on this level.

    This data is public (published by the ransomware group itself)
    and do not require sanitation.
    """

    source: str = Field(default="ransomlook")
    group_name: str = Field(description="Nom technique du groupe (ex: 'lockbit3')")
    group_display_name: str = Field(description="Nom affichable du groupe (ex: 'LockBit 3.0')")
    victim_name: str = Field(description="Nom de la victime tel qu'affiché sur le portail du groupe")
    victim_website: str | None = Field(
        default=None,
        description="Domaine de la victime si disponible",
    )
    discovered_at: datetime = Field(description="Date de découverte par RansomLook")
    published_at: datetime | None = Field(
        default=None,
        description="Date de publication sur le portail (si disponible)",
    )
    description: str | None = Field(
        default=None,
        description="Description publique publiée par le groupe (SANS données réelles)",
    )
    country: str | None = Field(default=None, description="Pays de la victime")
    activity: str | None = Field(default=None, description="Secteur d'activité")
    claim_size: str | None = Field(
        default=None,
        description="Taille des données revendiquées (ex: '500GB', '2TB')",
    )
    status: RansomStatus = Field(default=RansomStatus.UNKNOWN)

    # The .onion URL is stored but NEVER included in final reports
    portal_url: str | None = Field(
        default=None,
        description="URL .onion — stockée mais masquée dans les rapports",
        exclude=False,  # Included in the model but filtered in engine.py
    )

    search_term_matched: str = Field(description="Terme de recherche qui a déclenché ce matching")
    severity: str = Field(
        default="CRITICAL",
        description="Toujours CRITICAL — pas de négociation",
    )

    recommended_actions: list[str] = Field(
        default_factory=lambda: [
            "Activer immédiatement le Plan de Réponse aux Incidents (PRI)",
            "Isoler les systèmes potentiellement compromis du réseau",
            "Mandater un cabinet de forensics spécialisé ransomware",
            "Notifier la CNIL dans les 72h (Article 33 RGPD)",
            "NE PAS contacter le groupe ransomware sans conseil juridique",
            "Préserver tous les logs et artefacts système pour investigation",
        ],
        description="Actions critiques à entreprendre immédiatement",
    )


class RansomStats(BaseModel):
    """
    Statistics of the local RansomLook instance.
    Returned by GET /api/v1/stats.
    """

    groups_tracked: int = Field(default=0, description="Nombre de groupes ransomware suivis")
    total_posts: int = Field(default=0, description="Nombre total de victimes indexées")
    last_update: datetime | None = Field(
        default=None,
        description="Date du dernier cycle de scraping",
    )
    instance_url: str = Field(description="URL de l'instance RansomLook")
    mode: str = Field(default="local", description="Mode d'utilisation (local ou saas)")
    is_healthy: bool = Field(
        default=False,
        description="True si l'instance est joignable et fonctionnelle",
    )
