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
        architecture_score = analysis_results.get('architecture_score')
        score_display = f"{architecture_score}/100" if architecture_score is not None else "Unavailable"
        content = f"""
## Architecture Overview

**Architecture Score:** {score_display}

**Architecture Type:** {analysis_results.get('architecture_type') or 'Unknown'}

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
        dependency_health = analysis_results.get('dependency_health_score')
        score_display = f"{dependency_health}/100" if dependency_health is not None else "Unavailable"
        circ_deps = analysis_results.get('circular_dependencies')
        circ_display = str(circ_deps) if circ_deps is not None else "Unavailable"
        content = f"""
## Dependency Analysis

**Dependency Health Score:** {score_display}

**Total Dependencies:** {len(analysis_results.get('dependencies', []))}

**Circular Dependencies:** {circ_display}
"""
        return ReportSection(title="Dependency Analysis", content=content.strip(), score=dependency_health)

    def _build_database_schema_summary(self, analysis_results: dict[str, Any]) -> ReportSection:
        """Build database schema summary section."""
        schema_score = analysis_results.get('schema_score')
        score_display = f"{schema_score}/100" if schema_score is not None else "Unavailable"
        entities = analysis_results.get('entities')
        relationships = analysis_results.get('relationships')
        content = f"""
## Database Schema Summary

**Schema Score:** {score_display}

**Entities Detected:** {str(entities) if entities is not None else 'Unavailable'}

**Relationships Detected:** {str(relationships) if relationships is not None else 'Unavailable'}
"""
        return ReportSection(title="Database Schema Summary", content=content.strip(), score=schema_score)

    def _build_api_flow_summary(self, analysis_results: dict[str, Any]) -> ReportSection:
        """Build API flow summary section."""
        flow_score = analysis_results.get('flow_score')
        score_display = f"{flow_score}/100" if flow_score is not None else "Unavailable"
        endpoints = analysis_results.get('endpoints')
        controllers = analysis_results.get('controllers')
        content = f"""
## API Flow Summary

**API Flow Score:** {score_display}

**Endpoints Detected:** {str(endpoints) if endpoints is not None else 'Unavailable'}

**Controllers Detected:** {str(controllers) if controllers is not None else 'Unavailable'}
"""
        return ReportSection(title="API Flow Summary", content=content.strip(), score=flow_score)

    def _build_security_summary(self, analysis_results: dict[str, Any]) -> ReportSection:
        """Build security summary section."""
        security_score = analysis_results.get('security_score')
        score_display = f"{security_score}/100" if security_score is not None else "Unavailable"
        vulns = analysis_results.get('vulnerabilities')
        content = f"""
## Security Summary

**Security Score:** {score_display}

**Vulnerabilities Found:** {str(vulns) if vulns is not None else 'Unavailable'}

**Security Issues:** {len(analysis_results.get('security_issues', []))}
"""
        return ReportSection(title="Security Summary", content=content.strip(), score=security_score)

    def _build_quality_summary(self, analysis_results: dict[str, Any]) -> ReportSection:
        """Build quality summary section."""
        quality_score = analysis_results.get('quality_score')
        score_display = f"{quality_score}/100" if quality_score is not None else "Unavailable"
        smells = analysis_results.get('code_smells')
        maint = analysis_results.get('maintainability_index')
        content = f"""
## Quality Summary

**Quality Score:** {score_display}

**Code Smells:** {str(smells) if isinstance(smells, int) else 'Unavailable'}

**Maintainability Index:** {str(maint) if maint is not None else 'Unavailable'}
"""
        return ReportSection(title="Quality Summary", content=content.strip(), score=quality_score)

    def _build_risk_summary(self, analysis_results: dict[str, Any]) -> ReportSection:
        """Build risk summary section."""
        risk_score = analysis_results.get('risk_score')
        score_display = f"{risk_score}/100" if risk_score is not None else "Unavailable"
        content = f"""
## Risk Summary

**Risk Score:** {score_display}

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
        solid_score = analysis_results.get('solid_score')
        score_display = f"{solid_score}/100" if solid_score is not None else "Unavailable"
        content = f"""
## SOLID Principles Summary

**Overall SOLID Score:** {score_display}

**SRP Score:** {analysis_results.get('srp_score') or 'Unavailable'}

**OCP Score:** {analysis_results.get('ocp_score') or 'Unavailable'}

**LSP Score:** {analysis_results.get('lsp_score') or 'Unavailable'}

**ISP Score:** {analysis_results.get('isp_score') or 'Unavailable'}

**DIP Score:** {analysis_results.get('dip_score') or 'Unavailable'}
"""
        return ReportSection(title="SOLID Principles Summary", content=content.strip(), score=solid_score)

    def _build_microservice_readiness(self, analysis_results: dict[str, Any]) -> ReportSection:
        """Build microservice readiness section."""
        microservice_score = analysis_results.get('microservice_score')
        score_display = f"{microservice_score}/100" if microservice_score is not None else "Unavailable"
        cands = analysis_results.get('service_candidates')
        recs = analysis_results.get('recommended_services')
        content = f"""
## Microservice Readiness

**Microservice Score:** {score_display}

**Service Candidates:** {str(cands) if cands is not None else 'Unavailable'}

**Recommended Services:** {str(recs) if recs is not None else 'Unavailable'}
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
