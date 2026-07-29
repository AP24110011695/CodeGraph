"""Report builder for architecture report engine.

Builds comprehensive architecture report sections.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ReportSection:
    """A section of the architecture report."""

    title: str
    content: str
    score: int | None = None


class ReportBuilder:
    """Builds architecture report sections from analysis results.

    Reuses outputs from all previous analysis engines.
    """

    def __init__(self):
        """Initialize the report builder."""
        pass

    def build_report(
        self,
        project_path: Path,
        analysis_results: dict[str, Any],
    ) -> list[ReportSection]:
        """Build comprehensive architecture report.

        Args:
            project_path: The project path.
            analysis_results: Dictionary of analysis results from all engines.

        Returns:
            List of report sections.
        """
        sections: list[ReportSection] = []

        # Add repository overview
        sections.append(self._build_repository_overview(project_path, analysis_results))

        # Add technology stack
        sections.append(self._build_technology_stack(analysis_results))

        # Add architecture overview
        sections.append(self._build_architecture_overview(analysis_results))

        # Add layer analysis
        sections.append(self._build_layer_analysis(analysis_results))

        # Add dependency analysis
        sections.append(self._build_dependency_analysis(analysis_results))

        # Add database schema summary
        sections.append(self._build_database_schema_summary(analysis_results))

        # Add API flow summary
        sections.append(self._build_api_flow_summary(analysis_results))

        # Add security summary
        sections.append(self._build_security_summary(analysis_results))

        # Add quality summary
        sections.append(self._build_quality_summary(analysis_results))

        # Add risk summary
        sections.append(self._build_risk_summary(analysis_results))

        # Add design pattern summary
        sections.append(self._build_design_pattern_summary(analysis_results))

        # Add SOLID summary
        sections.append(self._build_solid_summary(analysis_results))

        # Add microservice readiness
        sections.append(self._build_microservice_readiness(analysis_results))

        # Add code smell summary
        sections.append(self._build_code_smell_summary(analysis_results))

        # Add architecture recommendations
        sections.append(self._build_architecture_recommendations(analysis_results))

        return sections

    def _build_repository_overview(self, project_path: Path, analysis_results: dict[str, Any]) -> ReportSection:
        """Build repository overview section."""
        content = f"""
## Repository Overview

**Project Path:** {project_path}

**Total Files:** {analysis_results.get('total_files', 'N/A')}

**Total Lines of Code:** {analysis_results.get('total_lines', 'N/A')}

**Languages Detected:** {', '.join(analysis_results.get('languages', []))}
"""
        return ReportSection(title="Repository Overview", content=content.strip())

    def _build_technology_stack(self, analysis_results: dict[str, Any]) -> ReportSection:
        """Build technology stack section."""
        framework = analysis_results.get('framework', 'Unknown')
        content = f"""
## Technology Stack

**Primary Framework:** {framework}

**Dependencies:** {len(analysis_results.get('dependencies', []))}

**Database:** {analysis_results.get('database', 'Not detected')}
"""
        return ReportSection(title="Technology Stack", content=content.strip())

    def _build_architecture_overview(self, analysis_results: dict[str, Any]) -> ReportSection:
        """Build architecture overview section."""
        architecture_score = analysis_results.get('architecture_score', 0)
        content = f"""
## Architecture Overview

**Architecture Score:** {architecture_score}/100

**Architecture Type:** {analysis_results.get('architecture_type', 'Unknown')}

**Layers Detected:** {len(analysis_results.get('layers', []))}
"""
        return ReportSection(title="Architecture Overview", content=content.strip(), score=architecture_score)

    def _build_layer_analysis(self, analysis_results: dict[str, Any]) -> ReportSection:
        """Build layer analysis section."""
        layers = analysis_results.get('layers', [])
        content = f"""
## Layer Analysis

**Layers Detected:** {len(layers)}

{self._format_list(layers)}
"""
        return ReportSection(title="Layer Analysis", content=content.strip())

    def _build_dependency_analysis(self, analysis_results: dict[str, Any]) -> ReportSection:
        """Build dependency analysis section."""
        dependency_health = analysis_results.get('dependency_health_score', 0)
        content = f"""
## Dependency Analysis

**Dependency Health Score:** {dependency_health}/100

**Total Dependencies:** {len(analysis_results.get('dependencies', []))}

**Circular Dependencies:** {analysis_results.get('circular_dependencies', 0)}
"""
        return ReportSection(title="Dependency Analysis", content=content.strip(), score=dependency_health)

    def _build_database_schema_summary(self, analysis_results: dict[str, Any]) -> ReportSection:
        """Build database schema summary section."""
        schema_score = analysis_results.get('schema_score', 0)
        content = f"""
## Database Schema Summary

**Schema Score:** {schema_score}/100

**Entities Detected:** {analysis_results.get('entities', 0)}

**Relationships Detected:** {analysis_results.get('relationships', 0)}
"""
        return ReportSection(title="Database Schema Summary", content=content.strip(), score=schema_score)

    def _build_api_flow_summary(self, analysis_results: dict[str, Any]) -> ReportSection:
        """Build API flow summary section."""
        flow_score = analysis_results.get('flow_score', 0)
        content = f"""
## API Flow Summary

**API Flow Score:** {flow_score}/100

**Endpoints Detected:** {analysis_results.get('endpoints', 0)}

**Controllers Detected:** {analysis_results.get('controllers', 0)}
"""
        return ReportSection(title="API Flow Summary", content=content.strip(), score=flow_score)

    def _build_security_summary(self, analysis_results: dict[str, Any]) -> ReportSection:
        """Build security summary section."""
        security_score = analysis_results.get('security_score', 0)
        content = f"""
## Security Summary

**Security Score:** {security_score}/100

**Vulnerabilities Found:** {analysis_results.get('vulnerabilities', 0)}

**Security Issues:** {len(analysis_results.get('security_issues', []))}
"""
        return ReportSection(title="Security Summary", content=content.strip(), score=security_score)

    def _build_quality_summary(self, analysis_results: dict[str, Any]) -> ReportSection:
        """Build quality summary section."""
        quality_score = analysis_results.get('quality_score', 0)
        content = f"""
## Quality Summary

**Quality Score:** {quality_score}/100

**Code Smells:** {analysis_results.get('code_smells', 0)}

**Maintainability Index:** {analysis_results.get('maintainability_index', 'N/A')}
"""
        return ReportSection(title="Quality Summary", content=content.strip(), score=quality_score)

    def _build_risk_summary(self, analysis_results: dict[str, Any]) -> ReportSection:
        """Build risk summary section."""
        risk_score = analysis_results.get('risk_score', 0)
        content = f"""
## Risk Summary

**Risk Score:** {risk_score}/100

**High Risk Areas:** {len(analysis_results.get('high_risk_areas', []))}

**Risk Factors:** {len(analysis_results.get('risk_factors', []))}
"""
        return ReportSection(title="Risk Summary", content=content.strip(), score=risk_score)

    def _build_design_pattern_summary(self, analysis_results: dict[str, Any]) -> ReportSection:
        """Build design pattern summary section."""
        patterns = analysis_results.get('design_patterns', {})
        content = f"""
## Design Pattern Summary

**Patterns Detected:** {len(patterns.get('patterns', []))}

**Anti-Patterns Detected:** {len(patterns.get('anti_patterns', []))}
"""
        return ReportSection(title="Design Pattern Summary", content=content.strip())

    def _build_solid_summary(self, analysis_results: dict[str, Any]) -> ReportSection:
        """Build SOLID summary section."""
        solid_score = analysis_results.get('solid_score', 0)
        content = f"""
## SOLID Principles Summary

**Overall SOLID Score:** {solid_score}/100

**SRP Score:** {analysis_results.get('srp_score', 'N/A')}

**OCP Score:** {analysis_results.get('ocp_score', 'N/A')}

**LSP Score:** {analysis_results.get('lsp_score', 'N/A')}

**ISP Score:** {analysis_results.get('isp_score', 'N/A')}

**DIP Score:** {analysis_results.get('dip_score', 'N/A')}
"""
        return ReportSection(title="SOLID Principles Summary", content=content.strip(), score=solid_score)

    def _build_microservice_readiness(self, analysis_results: dict[str, Any]) -> ReportSection:
        """Build microservice readiness section."""
        microservice_score = analysis_results.get('microservice_score', 0)
        content = f"""
## Microservice Readiness

**Microservice Score:** {microservice_score}/100

**Service Candidates:** {analysis_results.get('service_candidates', 0)}

**Recommended Services:** {analysis_results.get('recommended_services', 0)}
"""
        return ReportSection(title="Microservice Readiness", content=content.strip(), score=microservice_score)

    def _build_code_smell_summary(self, analysis_results: dict[str, Any]) -> ReportSection:
        """Build code smell summary section."""
        smells = analysis_results.get('code_smells', {})
        content = f"""
## Code Smell Summary

**Total Smells:** {len(smells.get('smells', []))}

**High Severity Smells:** {len(smells.get('high_severity', []))}
"""
        return ReportSection(title="Code Smell Summary", content=content.strip())

    def _build_architecture_recommendations(self, analysis_results: dict[str, Any]) -> ReportSection:
        """Build architecture recommendations section."""
        recommendations = analysis_results.get('recommendations', [])
        content = f"""
## Architecture Recommendations

{self._format_list(recommendations)}
"""
        return ReportSection(title="Architecture Recommendations", content=content.strip())

    def _format_list(self, items: list[str]) -> str:
        """Format a list as markdown."""
        if not items:
            return "None detected."
        return "\n".join(f"- {item}" for item in items[:10])  # Limit to 10 items


report_builder = ReportBuilder()
