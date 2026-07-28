"""License engine for license compliance analyzer.

Orchestrates license compliance analysis using all existing analysis modules.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.indexing.index_manager import IndexManager
from app.license.compliance_checker import ComplianceChecker, ComplianceFinding, ComplianceStatus, compliance_checker
from app.license.license_detector import LicenseDetector, LicenseInfo, license_detector
from app.services.scanner_service import ScanResult, scanner_service

logger = logging.getLogger(__name__)


@dataclass
class LicenseAnalysisResult:
    """Complete result from license compliance analysis."""

    project_name: str
    repository_license: str
    compliance_status: str
    summary: dict[str, int | str] = field(default_factory=dict)
    findings: list[dict] = field(default_factory=list)
    dependency_licenses: dict[str, str] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)


class LicenseEngine:
    """Performs comprehensive license compliance analysis.

    Reuses all existing CodeGraph analysis modules:
    - Repository Scanner
    - Framework Detector
    - Dependency Graph
    """

    def __init__(
        self,
        index_manager: IndexManager | None = None,
        license_detector: LicenseDetector | None = None,
        compliance_checker: ComplianceChecker | None = None,
    ):
        """Initialize the license engine.

        Args:
            index_manager: Optional IndexManager for accessing indexed repositories.
            license_detector: Optional LicenseDetector instance.
            compliance_checker: Optional ComplianceChecker instance.
        """
        self.index_manager = index_manager
        self.license_detector = license_detector or LicenseDetector()
        self.compliance_checker = compliance_checker or ComplianceChecker()

        # Individual analyzers
        self.scanner = scanner_service

    def analyze(
        self,
        project_path: Path,
        upload_id: str | None = None,
    ) -> LicenseAnalysisResult:
        """Perform comprehensive license compliance analysis for a repository.

        Args:
            project_path: Absolute path to the project directory.
            upload_id: Optional upload ID for accessing indexed data.

        Returns:
            LicenseAnalysisResult with comprehensive license compliance findings.

        Raises:
            FileNotFoundError: If project_path does not exist.
            NotADirectoryError: If project_path is not a directory.
        """
        project_path = project_path.resolve()

        if not project_path.exists():
            raise FileNotFoundError(f"Directory not found: {project_path}")

        if not project_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {project_path}")

        logger.info(f"Starting license compliance analysis for project: {project_path}")

        # Step 1: Scan the repository
        logger.info("Scanning repository")
        scan_result = self.scanner.scan(project_path)

        if scan_result.total_files == 0:
            logger.warning("Repository is empty, returning minimal result")
            return self._build_empty_result(scan_result)

        # Step 2: Detect repository license
        logger.info("Detecting repository license")
        repo_license_info = self.license_detector.detect_repository_license(project_path)
        repository_license = repo_license_info.license_name if repo_license_info else "Unknown"

        # Step 3: Detect dependency licenses
        logger.info("Detecting dependency licenses")
        dependency_licenses = self.license_detector.detect_dependency_licenses(project_path)

        # Step 4: Check compliance
        logger.info("Checking compliance")
        findings, compliance_status = self.compliance_checker.check_compliance(
            repository_license=repository_license if repository_license != "Unknown" else None,
            dependency_licenses=dependency_licenses,
        )

        # Step 5: Build summary
        summary = {
            "dependencies": len(dependency_licenses),
            "licensed": len([lic for lic in dependency_licenses.values() if lic != "Unknown"]),
            "unknown": len([lic for lic in dependency_licenses.values() if lic == "Unknown"]),
            "conflicts": compliance_status.conflicts,
        }

        # Step 6: Serialize findings
        serialized_findings = self._serialize_findings(findings)

        # Step 7: Generate recommendations
        recommendations = self._generate_recommendations(findings, repository_license, dependency_licenses)

        return LicenseAnalysisResult(
            project_name=scan_result.project_name,
            repository_license=repository_license,
            compliance_status=compliance_status.status,
            summary=summary,
            findings=serialized_findings,
            dependency_licenses=dependency_licenses,
            recommendations=recommendations,
        )

    def _build_empty_result(self, scan_result: ScanResult) -> LicenseAnalysisResult:
        """Build a minimal result for empty repositories."""
        return LicenseAnalysisResult(
            project_name=scan_result.project_name,
            repository_license="Unknown",
            compliance_status="UNKNOWN",
            summary={
                "dependencies": 0,
                "licensed": 0,
                "unknown": 0,
                "conflicts": 0,
            },
            findings=[],
            dependency_licenses={},
            recommendations=[],
        )

    def _serialize_findings(self, findings: list[ComplianceFinding]) -> list[dict]:
        """Serialize findings to dictionary format."""
        return [
            {
                "title": finding.title,
                "category": finding.category,
                "severity": finding.severity,
                "compliance_status": finding.compliance_status,
                "evidence": finding.evidence,
                "affected_files": finding.affected_files,
                "recommendation": finding.recommendation,
            }
            for finding in findings
        ]

    def _generate_recommendations(
        self,
        findings: list[ComplianceFinding],
        repository_license: str,
        dependency_licenses: dict[str, str],
    ) -> list[str]:
        """Generate improvement recommendations."""
        recommendations = []

        # Add recommendations from findings
        for finding in findings:
            if finding.recommendation and finding.recommendation not in recommendations:
                recommendations.append(finding.recommendation)

        # Add general recommendations
        if repository_license == "Unknown":
            recommendations.append("Add a LICENSE file to specify the repository's license.")

        unknown_count = len([lic for lic in dependency_licenses.values() if lic == "Unknown"])
        if unknown_count > 0:
            recommendations.append(f"Verify the licenses of {unknown_count} dependencies with unknown licenses.")

        if repository_license in ["MIT", "Apache-2.0", "BSD-3-Clause", "BSD-2-Clause", "ISC", "Unlicense"]:
            copyleft_count = len([lic for lic in dependency_licenses.values() if lic in ["GPL-3.0", "AGPL-3.0", "LGPL-3.0"]])
            if copyleft_count > 0:
                recommendations.append(f"Review the implications of {copyleft_count} copyleft dependencies on your permissive project.")

        return recommendations[:10]


license_engine = LicenseEngine()
