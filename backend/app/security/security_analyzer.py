"""Security Analyzer for CodeGraph.

Orchestrates security vulnerability analysis using the existing
scanner and rule-based detection engine.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path

from app.parsers.parser_engine import ParserEngine
from app.security.vulnerability_detector import SecurityDetectionResult, vulnerability_detector
from app.services.scanner_service import ScanResult, scanner_service

logger = logging.getLogger(__name__)


@dataclass
class SecurityAnalysisResult:
    """Complete result from security analysis."""
    
    summary: dict[str, int] = field(default_factory=dict)
    issues: list[dict] = field(default_factory=list)
    total_issues: int = 0


class SecurityAnalyzer:
    """Analyzes repositories for security vulnerabilities.
    
    Uses the existing pipeline:
    1. Repository Scanner
    2. Vulnerability Detector (rule-based)
    """
    
    def __init__(self):
        """Initialize the security analyzer."""
        self.vulnerability_detector = vulnerability_detector
    
    def analyze(
        self,
        project_path: Path,
        scan_result: ScanResult | None = None,
    ) -> SecurityAnalysisResult:
        """Analyze a project for security vulnerabilities.
        
        Args:
            project_path: Absolute path to the extracted project.
            scan_result: Optional pre-computed scan result.
        
        Returns:
            SecurityAnalysisResult with detected issues and summary.
        
        Raises:
            FileNotFoundError: If project_path does not exist.
            NotADirectoryError: If project_path is not a directory.
        """
        project_path = project_path.resolve()
        
        if not project_path.exists():
            raise FileNotFoundError(f"Directory not found: {project_path}")
        
        if not project_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {project_path}")
        
        # Step 1: Scan the repository (if not provided)
        if scan_result is None:
            logger.info(f"Scanning project: {project_path}")
            scan_result = scanner_service.scan(project_path)
        
        # Step 2: Parse the project (optional, for additional context)
        logger.info("Parsing project for additional context")
        try:
            parsing_result = ParserEngine.parse_project(project_path, scan_result)
        except Exception as e:
            logger.warning(f"Failed to parse project: {e}")
            parsing_result = None
        
        # Step 3: Detect vulnerabilities
        logger.info("Detecting security vulnerabilities")
        detection_result = self.vulnerability_detector.detect(
            project_path, scan_result, parsing_result
        )
        
        # Step 4: Build result
        result = SecurityAnalysisResult(
            summary=detection_result.summary,
            issues=[self._issue_to_dict(issue) for issue in detection_result.issues],
            total_issues=len(detection_result.issues),
        )
        
        return result
    
    def _issue_to_dict(self, issue) -> dict:
        """Convert a SecurityIssue to a dictionary."""
        return {
            "severity": issue.severity,
            "rule": issue.rule,
            "file": issue.file,
            "line": issue.line,
            "description": issue.description,
            "language": issue.language,
        }


security_analyzer = SecurityAnalyzer()
