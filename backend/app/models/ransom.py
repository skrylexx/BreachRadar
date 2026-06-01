"""
breachradar/models/ransom.py

Modèles Pydantic spécifiques à RansomLook.

NOTE DE SÉCURITÉ IMPORTANTE :
Les données RansomLook sont PUBLIQUES par nature — elles sont publiées
délibérément par les groupes ransomware sur leurs portails d'extorsion.
Ces données ne nécessitent PAS de sanitisation (contrairement aux données
email/password des autres sources).

Cependant, l'URL .onion du portail ransomware n'est PAS incluse dans les
rapports finaux (stockée mais masquée), pour éviter de faciliter l'accès
direct à ces portails.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class RansomStatus(StrEnum):
    """
    Statut de la publication de la victime sur le portail ransomware.
    Basé sur les métadonnées publiques disponibles via RansomLook.
    """

    LISTED = "LISTED"  # Victime listée, données pas encore publiées
    PUBLISHED = "PUBLISHED"  # Données publiées / téléchargeables
    REMOVED = "REMOVED"  # Publication supprimée (rançon payée ?)
    UNKNOWN = "UNKNOWN"


class RansomFinding(BaseModel):
    """
    Résultat d'une correspondance RansomLook.

    ⚠️  ALERTE DE NIVEAU MAXIMAL : un RansomFinding indique qu'une
    exfiltration massive est probable ou en cours. La sévérité est
    TOUJOURS CRITICAL — aucune négociation possible sur ce niveau.

    Ces données sont publiques (publiées par le groupe ransomware lui-même)
    et ne nécessitent pas de sanitisation.
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

    # L'URL .onion est stockée mais JAMAIS incluse dans les rapports finaux
    portal_url: str | None = Field(
        default=None,
        description="URL .onion — stockée mais masquée dans les rapports",
        exclude=False,  # Incluse dans le modèle mais filtrée dans engine.py
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
    Statistiques de l'instance RansomLook locale.
    Retournées par GET /api/v1/stats.
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
