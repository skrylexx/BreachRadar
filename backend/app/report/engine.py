"""
breachradar/report/engine.py

Reporting engine.
Uses Jinja2 to generate Markdown and HTML reports, and Pydantic for JSON.
RULE: .onion URLs (portal_url) must be hidden in the Markdown/HTML report.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.models.report import FinalReport

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).parent / "templates"


class ReportEngine:
    """
    Report generator (JSON, Markdown, HTML).
    """

    def __init__(self, output_dir: str | Path = "./reports") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        if not TEMPLATES_DIR.exists():
            logger.warning(f"Répertoire des templates introuvable: {TEMPLATES_DIR}")

        self.env = Environment(  # nosemgrep
            loader=FileSystemLoader(str(TEMPLATES_DIR)) if TEMPLATES_DIR.exists() else None,
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=select_autoescape(["html", "xml"]),
        )

        # Custom filter to hide .onion URLs
        self.env.filters["mask_onion"] = self._mask_onion_url

    @staticmethod
    def _mask_onion_url(url: str | None) -> str:
        """Hides the .onion URL to prevent easy access to ransomware portals."""
        if not url:
            return "N/A"
        if ".onion" in url:
            return "[URL .onion MASQUÉE POUR SÉCURITÉ]"
        return url

    def generate(self, report: FinalReport, formats: list[str]) -> list[Path]:
        """
        Generates reports in requested formats.

        Args:
            report: Pydantic template of the final report
            formats: List of formats (ex: ["json", "markdown", "html"])

        Returns:
            List of paths to generated files
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
                    file_path = self._generate_template(report, f"{base_filename}.md", "report.md.j2")
                    generated_files.append(file_path)
                elif fmt == "html":
                    file_path = self._generate_template(report, f"{base_filename}.html", "report.html.j2")
                    generated_files.append(file_path)
                elif fmt == "pdf":
                    file_path = self._generate_pdf(report, f"{base_filename}.pdf")
                    generated_files.append(file_path)
                else:
                    logger.warning(f"Format de rapport non supporté: {fmt}")
            except Exception as e:
                logger.error(f"Échec de génération du rapport {fmt}: {e}")

        logger.info(f"Rapports générés dans {self.output_dir}")
        return generated_files

    def _generate_json(self, report: FinalReport, base_filename: str) -> Path:
        """Generates the report in JSON format."""
        file_path = self.output_dir / f"{base_filename}.json"

        # Serialization with Pydantic
        report_json = report.model_dump_json(indent=2)

        # For JSON, we can choose to purge the portal_url too or do we keep it for API use?
        # The FinalReport template does not exclude portal_url. To be strict, we can hide it manually here.
        # But the test 'test_ransom_finding_portal_url_stored_but_visible' says:
        # "The .onion URL is stored in RansomFinding.portal_url but the ReportEngine MUST hide it when generating the report."

        data = json.loads(report_json)
        # Recursive masking of portal_url
        if "ransomware_alerts" in data and "alerts" in data["ransomware_alerts"]:
            for alert in data["ransomware_alerts"]["alerts"]:
                if alert.get("portal_url") and ".onion" in alert["portal_url"]:
                    alert["portal_url"] = "[URL .onion MASQUÉE POUR SÉCURITÉ]"

        with file_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return file_path

    def _generate_template(self, report: FinalReport, filename: str, template_name: str) -> Path:
        """Generates a report based on a Jinja2 template."""
        if not TEMPLATES_DIR.exists():
            raise FileNotFoundError("Répertoire des templates introuvable. Impossible de générer le rapport.")

        template = self.env.get_template(template_name)
        content = template.render(report=report)

        output_path = self.output_dir / filename
        with output_path.open("w", encoding="utf-8") as f:
            f.write(content)

        logger.info(f"Rapport généré: {output_path}")
        return output_path

    def _generate_pdf(self, report: FinalReport, filename: str) -> Path:
        """Generates a PDF report via WeasyPrint (using the HTML template)."""
        output_path = self.output_dir / filename

        try:
            from weasyprint import HTML

            # We make the HTML complete
            template = self.env.get_template("report.html.j2")
            html_content = template.render(report=report)

            # Using WeasyPrint to generate the PDF
            # base_url allows you to resolve local assets if necessary
            HTML(string=html_content).write_pdf(output_path)
            logger.info(f"Rapport PDF généré: {output_path}")
            return output_path

        except (ImportError, Exception) as e:
            logger.error(f"Échec de génération PDF: {e}")
            # Fallback: we just generate the HTML
            html_filename = filename.replace(".pdf", ".html")
            logger.info(f"Génération du HTML en fallback: {html_filename}")
            return self._generate_template(report, html_filename, "report.html.j2")
