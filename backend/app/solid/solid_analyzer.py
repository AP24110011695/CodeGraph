"""SOLID analyzer for SOLID principle analyzer.

Analyzes SOLID principles from repository analysis.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.solid.principle_checker import PrincipleChecker, PrincipleResult, principle_checker

logger = logging.getLogger(__name__)


@dataclass
class SOLIDAnalysisResult:
    """Complete result from SOLID analysis."""

    srp_result: PrincipleResult
    ocp_result: PrincipleResult
    lsp_result: PrincipleResult
    isp_result: PrincipleResult
    dip_result: PrincipleResult
    overall_score: int
    overall_rating: str
    priority_fixes: list[str]


class SOLIDAnalyzer:
    """Analyzes SOLID principles from repository analysis.

    Reuses outputs from:
    - Code Smell Detector
    - Parser Engine
    - Dependency Graph
    - Design Pattern Detector
    """

    def __init__(self, principle_checker: PrincipleChecker | None = None):
        """Initialize the SOLID analyzer.

        Args:
            principle_checker: Optional PrincipleChecker instance.
        """
        self.principle_checker = principle_checker or PrincipleChecker()

    def analyze(
        self,
        project_path: Path,
        smell_findings: list[dict] | None = None,
        parsing_result: Any | None = None,
        dependency_graph: dict | None = None,
    ) -> SOLIDAnalysisResult:
        """Analyze SOLID principles for a repository.

        Args:
            project_path: Absolute path to the project directory.
            smell_findings: Findings from code smell detector.
            parsing_result: Result from parser engine.
            dependency_graph: Dependency graph from dependency builder.

        Returns:
            SOLIDAnalysisResult with comprehensive SOLID analysis.
        """
        logger.info("Analyzing SOLID principles")

        # Check each principle
        srp_result = self.principle_checker.check_srp(project_path, smell_findings, parsing_result)
        ocp_result = self.principle_checker.check_ocp(project_path, parsing_result)
        lsp_result = self.principle_checker.check_lsp(project_path, parsing_result)
        isp_result = self.principle_checker.check_isp(project_path, parsing_result)
        dip_result = self.principle_checker.check_dip(project_path, dependency_graph)

        # Calculate overall score
        overall_score = self._calculate_overall_score(
            srp_result, ocp_result, lsp_result, isp_result, dip_result
        )

        # Determine overall rating
        overall_rating = self._determine_overall_rating(overall_score)

        # Generate priority fixes
        priority_fixes = self._generate_priority_fixes(
            srp_result, ocp_result, lsp_result, isp_result, dip_result
        )

        return SOLIDAnalysisResult(
            srp_result=srp_result,
            ocp_result=ocp_result,
            lsp_result=lsp_result,
            isp_result=isp_result,
            dip_result=dip_result,
            overall_score=overall_score,
            overall_rating=overall_rating,
            priority_fixes=priority_fixes,
        )

    def _calculate_overall_score(
        self,
        srp_result: PrincipleResult,
        ocp_result: PrincipleResult,
        lsp_result: PrincipleResult,
        isp_result: PrincipleResult,
        dip_result: PrincipleResult,
    ) -> int:
        """Calculate overall SOLID score.

        Args:
            srp_result: SRP result.
            ocp_result: OCP result.
            lsp_result: LSP result.
            isp_result: ISP result.
            dip_result: DIP result.

        Returns:
            Overall score (0-100).
        """
        # Weighted average of all principle scores
        weights = {
            "srp": 0.25,
            "ocp": 0.2,
            "lsp": 0.2,
            "isp": 0.15,
            "dip": 0.2,
        }

        overall_score = (
            srp_result.score * weights["srp"] +
            ocp_result.score * weights["ocp"] +
            lsp_result.score * weights["lsp"] +
            isp_result.score * weights["isp"] +
            dip_result.score * weights["dip"]
        )

        return int(overall_score)

    def _determine_overall_rating(self, overall_score: int) -> str:
        """Determine overall rating from score.

        Args:
            overall_score: The overall score.

        Returns:
            Overall rating.
        """
        if overall_score >= 90:
            return "Excellent"
        elif overall_score >= 75:
            return "Good"
        elif overall_score >= 60:
            return "Fair"
        else:
            return "Poor"

    def _generate_priority_fixes(
        self,
        srp_result: PrincipleResult,
        ocp_result: PrincipleResult,
        lsp_result: PrincipleResult,
        isp_result: PrincipleResult,
        dip_result: PrincipleResult,
    ) -> list[str]:
        """Generate priority fixes from principle results.

        Args:
            srp_result: SRP result.
            ocp_result: OCP result.
            lsp_result: LSP result.
            isp_result: ISP result.
            dip_result: DIP result.

        Returns:
            List of priority fixes.
        """
        fixes = []

        # Add fixes from principles with violations
        for result in [srp_result, ocp_result, lsp_result, isp_result, dip_result]:
            if result.violations > 0:
                fixes.extend(result.recommendations)

        # Prioritize by severity
        return fixes[:10]  # Limit to top 10


solid_analyzer = SOLIDAnalyzer()
