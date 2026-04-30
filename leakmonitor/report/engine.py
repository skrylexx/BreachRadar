"""
leakmonitor/report/engine.py

Moteur de génération de rapports.
Utilise Jinja2 pour générer des rapports Markdown et HTML, et Pydantic pour le JSON.
RÈGLE : Les URL .onion (portal_url) doivent être masquées dans le rapport Markdown/HTML.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from leakmonitor.models.report import FinalReport

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).parent / "templates"


class ReportEngine:
    """
    Générateur de rapports (JSON, Markdown, HTML).
    """

    def __init__(self, output_dir: str | Path = "./reports") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        if not TEMPLATES_DIR.exists():
            logger.warning(f"Répertoire des templates introuvable: {TEMPLATES_DIR}")

        self.env = Environment(
            loader=FileSystemLoader(str(TEMPLATES_DIR)) if TEMPLATES_DIR.exists() else None,
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Filtre personnalisé pour masquer les URL .onion
        self.env.filters["mask_onion"] = self._mask_onion_url

    @staticmethod
    def _mask_onion_url(url: str | None) -> str:
        """Masque l'URL .onion pour ne pas faciliter l'accès aux portails ransomware."""
        if not url:
            return "N/A"
        if ".onion" in url:
            return "[URL .onion MASQUÉE POUR SÉCURITÉ]"
        return url

    def generate(self, report: FinalReport, formats: list[str]) -> list[Path]:
        """
        Génère les rapports dans les formats demandés.
        
        Args:
            report: Modèle Pydantic du rapport final
            formats: Liste des formats (ex: ["json", "markdown", "html"])
            
        Returns:
            Liste des chemins vers les fichiers générés
        """
        timestamp = report.report_metadata.generated_at.strftime("%Y%m%d_%H%M%S")
        domain = report.report_metadata.target_domain.replace(".", "_")
        base_filename = f"report_{domain}_{timestamp}"

        generated_files = []

        for fmt in formats:
            fmt = fmt.lower().strip()
            try:
                if fmt == "json":
                    file_path = self._generate_json(report, base_filename)
                    generated_files.append(file_path)
                elif fmt == "markdown" or fmt == "md":
                    file_path = self._generate_template(report, base_filename, "report.md.j2", "md")
                    generated_files.append(file_path)
                elif fmt == "html":
                    file_path = self._generate_template(report, base_filename, "report.html.j2", "html")
                    generated_files.append(file_path)
                else:
                    logger.warning(f"Format de rapport non supporté: {fmt}")
            except Exception as e:
                logger.error(f"Échec de génération du rapport {fmt}: {e}")

        logger.info(f"Rapports générés dans {self.output_dir}")
        return generated_files

    def _generate_json(self, report: FinalReport, base_filename: str) -> Path:
        """Génère le rapport au format JSON."""
        file_path = self.output_dir / f"{base_filename}.json"
        
        # Sérialisation avec Pydantic
        report_json = report.model_dump_json(indent=2)
        
        # Pour le JSON, on peut choisir de purger le portal_url aussi ou on le garde pour usage API?
        # Le modèle FinalReport n'exclut pas portal_url. Pour être strict, on peut le masquer manuellement ici.
        # Mais le test 'test_ransom_finding_portal_url_stored_but_visible' dit :
        # "L'URL .onion est stockée dans RansomFinding.portal_url mais le ReportEngine DOIT la masquer lors de la génération du rapport."
        
        data = json.loads(report_json)
        # Masquage récursif des portal_url
        if "ransomware_alerts" in data and "alerts" in data["ransomware_alerts"]:
            for alert in data["ransomware_alerts"]["alerts"]:
                if alert.get("portal_url") and ".onion" in alert["portal_url"]:
                    alert["portal_url"] = "[URL .onion MASQUÉE POUR SÉCURITÉ]"

        with file_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        return file_path

    def _generate_template(self, report: FinalReport, base_filename: str, template_name: str, ext: str) -> Path:
        """Génère un rapport basé sur un template Jinja2."""
        if not TEMPLATES_DIR.exists():
            raise FileNotFoundError(f"Répertoire des templates introuvable. Impossible de générer le rapport {ext}.")
            
        template = self.env.get_template(template_name)
        content = template.render(report=report)
        
        file_path = self.output_dir / f"{base_filename}.{ext}"
        with file_path.open("w", encoding="utf-8") as f:
            f.write(content)
            
        return file_path
