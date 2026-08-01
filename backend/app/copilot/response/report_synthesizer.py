"""Report synthesizer module.

Synthesizes comprehensive executive reports by merging data from multiple domains,
deduplicating content, and filtering internal metadata.
"""

import re
from typing import Dict, Any, List, Set, Tuple
from ..models.response_models import (
    CopilotResponse,
    IntentType,
    ArchitectureData,
    SecurityData,
    MetricsData,
    TimelineData,
    HealthData,
    AuthenticationData
)


class ReportSynthesizer:
    """Synthesizes comprehensive executive reports from multiple data sources."""
    
    def __init__(self) -> None:
        self._internal_patterns = [
            r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}',  # UUIDs
            r'repo_id["\']?\s*:\s*["\']?[a-zA-Z0-9_-]+',  # Repository IDs
            r'internal_id["\']?\s*:',  # Internal IDs
            r'payload["\']?\s*:',  # Payload keys
            r'data["\']?\s*:\s*\{',  # Raw data dictionaries
            r'statistics["\']?\s*:',  # Internal statistics
            r'engine["\']?\s*:',  # Engine names
            r'tool_output["\']?\s*:',  # Tool output keys
        ]
    
    def synthesize_executive_report(
        self,
        response: CopilotResponse,
        question: str,
        tool_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Synthesize a comprehensive executive report.
        
        Args:
            response: The copilot response with all extracted data
            question: The original user question
            tool_data: Raw tool data for extracting missing domain data
            
        Returns:
            Dictionary with synthesized report data
        """
        # For executive reports, we need ALL data from all domains
        # Extract any missing data if tool_data is provided
        if tool_data:
            from ..extractors.architecture import ArchitectureExtractor
            from ..extractors.security import SecurityExtractor
            from ..extractors.metrics import MetricsExtractor
            from ..extractors.timeline import TimelineExtractor
            
            arch_extractor = ArchitectureExtractor()
            sec_extractor = SecurityExtractor()
            metrics_extractor = MetricsExtractor()
            timeline_extractor = TimelineExtractor()
            
            if not response.architecture:
                response.architecture = arch_extractor.extract(tool_data)
            if not response.security:
                response.security = sec_extractor.extract(tool_data)
            if not response.metrics:
                response.metrics = metrics_extractor.extract(tool_data)
            if not response.timeline:
                response.timeline = timeline_extractor.extract(tool_data)
        
        report_data: Dict[str, Any] = {
            "executive_summary": self._generate_executive_summary(response),
            "repository_overview": self._generate_repository_overview(response),
            "architecture_assessment": self._generate_architecture_assessment(response),
            "repository_health": self._generate_repository_health(response),
            "security_findings": self._generate_security_findings(response),
            "timeline_activity": self._generate_timeline_activity(response),
            "highest_risk_areas": self._generate_highest_risk_areas(response),
            "recommended_actions": self._deduplicate_and_prioritize_recommendations(response),
            "suggested_refactoring": self._generate_suggested_refactoring(response),
            "overall_assessment": self._generate_overall_assessment(response)
        }
        
        return report_data
    
    def _filter_internal_data(self, text: str) -> str:
        """Remove internal metadata from text.
        
        Args:
            text: Text that may contain internal data
            
        Returns:
            Text with internal data removed
        """
        if not text:
            return text
        
        filtered = text
        for pattern in self._internal_patterns:
            filtered = re.sub(pattern, '[REDACTED]', filtered, flags=re.IGNORECASE)
        
        return filtered
    
    def _generate_executive_summary(self, response: CopilotResponse) -> str:
        """Generate a concise executive summary."""
        summary_parts = []
        
        # Architecture summary
        if response.architecture and response.architecture.module_count > 0:
            summary_parts.append(
                f"The repository consists of {response.architecture.module_count} modules "
                f"with {response.architecture.dependency_count} dependencies."
            )
        
        # Security summary
        if response.security and response.security.total_issues > 0:
            severity = "critical" if response.security.critical_issues else "significant"
            summary_parts.append(
                f"Security analysis identified {response.security.total_issues} {severity} issue(s) "
                f"requiring attention."
            )
        
        # Health summary
        if response.health:
            health_status = "good" if response.health.overall_score >= 7 else "needs improvement"
            summary_parts.append(
                f"Overall repository health is {health_status} (score: {response.health.overall_score:.1f}/10)."
            )
        
        # Timeline summary
        if response.timeline and response.timeline.commit_count > 0:
            summary_parts.append(
                f"Recent activity includes {response.timeline.commit_count} commits "
                f"across {len(response.timeline.files_changed)} files."
            )
        
        if not summary_parts:
            return "Repository analysis complete. See detailed sections below."
        
        return " ".join(summary_parts)
    
    def _generate_repository_overview(self, response: CopilotResponse) -> Dict[str, Any]:
        """Generate repository overview section."""
        overview = {
            "modules": response.architecture.module_count if response.architecture else 0,
            "dependencies": response.architecture.dependency_count if response.architecture else 0,
            "languages": [],
            "file_count": response.metrics.file_count if response.metrics else 0,
            "frameworks": response.metrics.frameworks if response.metrics else []
        }
        
        if response.metrics and response.metrics.languages:
            overview["languages"] = [
                {"name": lang, "count": count, "percentage": self._calculate_percentage(count, response.metrics.languages)}
                for lang, count in response.metrics.languages
            ]
        
        return overview
    
    def _generate_architecture_assessment(self, response: CopilotResponse) -> Dict[str, Any]:
        """Generate architecture assessment section."""
        if not response.architecture:
            return {"status": "No architecture data available"}
        
        assessment = {
            "module_count": response.architecture.module_count,
            "dependency_count": response.architecture.dependency_count,
            "layers": response.architecture.layers,
            "coupled_modules": response.architecture.coupled_modules[:5],  # Top 5 only
            "assessment": self._assess_architecture_quality(response.architecture)
        }
        
        return assessment
    
    def _generate_repository_health(self, response: CopilotResponse) -> Dict[str, Any]:
        """Generate repository health section."""
        if not response.health:
            return {"status": "No health data available"}
        
        return {
            "architecture_score": response.health.architecture_score,
            "architecture_description": response.health.architecture_description,
            "security_score": response.health.security_score,
            "security_description": response.health.security_description,
            "quality_score": response.health.quality_score,
            "quality_description": response.health.quality_description,
            "dependency_score": response.health.dependency_score,
            "dependency_description": response.health.dependency_description,
            "overall_score": response.health.overall_score,
            "risks": response.health.risks
        }
    
    def _generate_security_findings(self, response: CopilotResponse) -> Dict[str, Any]:
        """Generate security findings section."""
        if not response.security:
            return {"status": "No security data available"}
        
        findings = {
            "total_issues": response.security.total_issues,
            "severity_breakdown": response.security.severity_breakdown,
            "critical_issues": response.security.critical_issues[:3],  # Top 3 only
            "high_issues": response.security.high_issues[:5],  # Top 5 only
            "affected_files": response.security.affected_files[:10],  # Top 10 only
            "risk_assessment": self._assess_security_risk(response.security)
        }
        
        return findings
    
    def _generate_timeline_activity(self, response: CopilotResponse) -> Dict[str, Any]:
        """Generate timeline and recent activity section."""
        if not response.timeline:
            return {"status": "No timeline data available"}
        
        return {
            "commit_count": response.timeline.commit_count,
            "recent_commits": response.timeline.recent_commits[:5],  # Top 5 only
            "files_changed": response.timeline.files_changed[:10],  # Top 10 only
            "affected_subsystems": response.timeline.affected_subsystems[:5],  # Top 5 only
            "activity_summary": self._summarize_activity(response.timeline)
        }
    
    def _generate_highest_risk_areas(self, response: CopilotResponse) -> List[Dict[str, Any]]:
        """Generate highest risk areas section."""
        risk_areas = []
        
        # Security risks
        if response.security and response.security.critical_issues:
            for issue in response.security.critical_issues[:3]:
                risk_areas.append({
                    "area": issue.get("file", "Unknown"),
                    "type": issue.get("type", "Security Issue"),
                    "severity": "critical",
                    "impact": "High - Immediate action required"
                })
        
        # Architecture risks (coupled modules)
        if response.architecture and response.architecture.coupled_modules:
            for module in response.architecture.coupled_modules[:3]:
                risk_areas.append({
                    "area": module,
                    "type": "High Coupling",
                    "severity": "high",
                    "impact": "Medium - Refactoring recommended"
                })
        
        # Health risks
        if response.health and response.health.risks:
            for risk in response.health.risks[:3]:
                risk_areas.append({
                    "area": "Repository Health",
                    "type": risk,
                    "severity": "medium",
                    "impact": "Medium - Monitor and address"
                })
        
        return risk_areas[:5]  # Top 5 only
    
    def _deduplicate_and_prioritize_recommendations(self, response: CopilotResponse) -> List[Dict[str, Any]]:
        """Deduplicate and prioritize recommendations."""
        all_recommendations = response.recommendations.copy()
        
        # Deduplicate
        seen: Set[str] = set()
        unique_recommendations = []
        for rec in all_recommendations:
            normalized = rec.lower().strip()
            if normalized not in seen:
                seen.add(normalized)
                unique_recommendations.append(rec)
        
        # Prioritize (critical first, then by length/complexity)
        prioritized = sorted(
            unique_recommendations,
            key=lambda x: (
                0 if any(word in x.lower() for word in ['critical', 'urgent', 'immediate', 'patch']) else
                1 if any(word in x.lower() for word in ['security', 'vulnerability', 'risk']) else
                2 if any(word in x.lower() for word in ['architecture', 'coupling', 'refactor']) else
                3
            )
        )
        
        # Convert to structured format
        structured = []
        for i, rec in enumerate(prioritized[:5], 1):  # Top 5 only
            priority = "Critical" if i == 1 else "High" if i <= 2 else "Medium"
            structured.append({
                "priority": priority,
                "action": rec,
                "rationale": self._generate_rationale(rec)
            })
        
        return structured
    
    def _generate_suggested_refactoring(self, response: CopilotResponse) -> List[Dict[str, Any]]:
        """Generate suggested refactoring section."""
        refactorings = []
        
        if response.architecture and response.architecture.coupled_modules:
            for module in response.architecture.coupled_modules[:3]:
                refactorings.append({
                    "target": module,
                    "type": "Reduce Coupling",
                    "description": f"Extract shared functionality from {module} to reduce dependencies",
                    "effort": "Medium",
                    "impact": "High"
                })
        
        if response.metrics and response.metrics.file_count > 1000:
            refactorings.append({
                "target": "Large Directories",
                "type": "Modularization",
                "description": "Break down large directories into smaller, focused modules",
                "effort": "High",
                "impact": "High"
            })
        
        if response.security and response.security.total_issues > 5:
            refactorings.append({
                "target": "Security Code",
                "type": "Security Hardening",
                "description": "Implement security best practices and address vulnerabilities",
                "effort": "Medium",
                "impact": "Critical"
            })
        
        return refactorings[:5]  # Top 5 only
    
    def _generate_overall_assessment(self, response: CopilotResponse) -> Dict[str, Any]:
        """Generate overall engineering assessment."""
        assessment = {
            "overall_score": 0,
            "strengths": [],
            "weaknesses": [],
            "next_steps": []
        }
        
        # Calculate overall score
        if response.health:
            assessment["overall_score"] = response.health.overall_score
        
        # Identify strengths
        if response.architecture and response.architecture.module_count > 0:
            assessment["strengths"].append("Modular architecture with clear separation of concerns")
        
        if response.security and response.security.total_issues == 0:
            assessment["strengths"].append("No security vulnerabilities detected")
        
        if response.metrics and len(response.metrics.languages) <= 3:
            assessment["strengths"].append("Consistent technology stack")
        
        # Identify weaknesses
        if response.security and response.security.total_issues > 5:
            assessment["weaknesses"].append("Multiple security issues require attention")
        
        if response.architecture and len(response.architecture.coupled_modules) > 3:
            assessment["weaknesses"].append("High coupling between modules impacts maintainability")
        
        if response.health and response.health.overall_score < 7:
            assessment["weaknesses"].append("Overall health score below target threshold")
        
        # Next steps
        assessment["next_steps"] = [
            "Address critical security vulnerabilities",
            "Refactor highly coupled modules",
            "Implement automated security scanning",
            "Schedule regular health assessments"
        ]
        
        return assessment
    
    def _calculate_percentage(self, count: int, languages: List[Tuple[str, int]]) -> float:
        """Calculate percentage for a language count."""
        total = sum(c for _, c in languages)
        return (count / total * 100) if total > 0 else 0
    
    def _assess_architecture_quality(self, arch_data: ArchitectureData) -> str:
        """Assess architecture quality."""
        if arch_data.module_count == 0:
            return "No architecture data available"
        
        if len(arch_data.coupled_modules) > 5:
            return "High coupling detected - refactoring recommended"
        elif len(arch_data.coupled_modules) > 2:
            return "Moderate coupling - monitor and address"
        else:
            return "Well-structured architecture with manageable complexity"
    
    def _assess_security_risk(self, sec_data: SecurityData) -> str:
        """Assess security risk level."""
        if sec_data.total_issues == 0:
            return "Low - No vulnerabilities detected"
        elif sec_data.total_issues <= 5:
            return "Medium - Address issues promptly"
        elif sec_data.total_issues <= 15:
            return "High - Immediate attention required"
        else:
            return "Critical - Urgent remediation needed"
    
    def _summarize_activity(self, timeline_data: TimelineData) -> str:
        """Summarize timeline activity."""
        if timeline_data.commit_count == 0:
            return "No recent activity detected"
        
        return (
            f"{timeline_data.commit_count} commits across {len(timeline_data.files_changed)} files. "
            f"Activity focused on {len(timeline_data.affected_subsystems)} subsystem(s)."
        )
    
    def _generate_rationale(self, recommendation: str) -> str:
        """Generate rationale for a recommendation."""
        if "security" in recommendation.lower():
            return "Security vulnerabilities pose immediate risk to the application and user data"
        elif "architecture" in recommendation.lower() or "coupling" in recommendation.lower():
            return "High coupling reduces maintainability and increases change impact"
        elif "dependency" in recommendation.lower():
            return "Outdated dependencies may contain known vulnerabilities"
        elif "test" in recommendation.lower():
            return "Comprehensive testing prevents regressions and ensures quality"
        else:
            return "Improves overall code quality and maintainability"
