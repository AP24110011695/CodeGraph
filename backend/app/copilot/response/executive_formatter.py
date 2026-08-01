"""Executive report formatter module.

Formats synthesized report data into professional markdown reports
that resemble GitHub Advanced Security, SonarQube Enterprise, or Azure DevOps reports.
"""

from typing import Dict, Any, List
from ..models.response_models import CopilotResponse


class ExecutiveReportFormatter:
    """Formats executive reports with professional structure and formatting."""
    
    def format(self, report_data: Dict[str, Any], question: str) -> str:
        """Format synthesized report data as professional markdown.
        
        Args:
            report_data: Synthesized report data from ReportSynthesizer
            question: The original user question
            
        Returns:
            Professional markdown-formatted report
        """
        sections = []
        
        # Title
        sections.append("# Executive Engineering Report\n")
        
        # Executive Summary
        sections.append("## Executive Summary\n")
        sections.append(report_data.get("executive_summary", "No summary available"))
        sections.append("\n")
        
        # Repository Overview
        sections.append(self._format_repository_overview(report_data.get("repository_overview", {})))
        
        # Architecture Assessment
        sections.append(self._format_architecture_assessment(report_data.get("architecture_assessment", {})))
        
        # Repository Health
        sections.append(self._format_repository_health(report_data.get("repository_health", {})))
        
        # Security Findings
        sections.append(self._format_security_findings(report_data.get("security_findings", {})))
        
        # Timeline & Recent Activity
        sections.append(self._format_timeline_activity(report_data.get("timeline_activity", {})))
        
        # Highest Risk Areas
        sections.append(self._format_highest_risk_areas(report_data.get("highest_risk_areas", [])))
        
        # Recommended Actions
        sections.append(self._format_recommended_actions(report_data.get("recommended_actions", [])))
        
        # Suggested Refactoring
        sections.append(self._format_suggested_refactoring(report_data.get("suggested_refactoring", [])))
        
        # Overall Assessment
        sections.append(self._format_overall_assessment(report_data.get("overall_assessment", {})))
        
        return "\n".join(sections)
    
    def _format_repository_overview(self, overview: Dict[str, Any]) -> str:
        """Format repository overview section."""
        lines = ["## Repository Overview\n"]
        
        # Key metrics table
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Modules | {overview.get('modules', 0)} |")
        lines.append(f"| Dependencies | {overview.get('dependencies', 0)} |")
        lines.append(f"| Files | {overview.get('file_count', 0)} |")
        lines.append(f"| Languages | {len(overview.get('languages', []))} |")
        lines.append("")
        
        # Languages
        languages = overview.get('languages', [])
        if languages:
            lines.append("### Languages\n")
            lines.append("| Language | Files | Percentage |")
            lines.append("|----------|-------|------------|")
            for lang in languages[:5]:  # Top 5
                lines.append(f"| {lang.get('name', 'Unknown')} | {lang.get('count', 0)} | {lang.get('percentage', 0):.1f}% |")
            lines.append("")
        
        # Frameworks
        frameworks = overview.get('frameworks', [])
        if frameworks:
            lines.append("### Frameworks\n")
            for fw in frameworks[:5]:  # Top 5
                lines.append(f"- {fw}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_architecture_assessment(self, assessment: Dict[str, Any]) -> str:
        """Format architecture assessment section."""
        lines = ["## Architecture Assessment\n"]
        
        if "status" in assessment:
            lines.append(f"*{assessment['status']}*\n")
            return "\n".join(lines)
        
        # Key metrics
        lines.append("### Architecture Metrics\n")
        lines.append(f"- **Modules**: {assessment.get('module_count', 0)}")
        lines.append(f"- **Dependencies**: {assessment.get('dependency_count', 0)}")
        lines.append(f"- **Layers**: {len(assessment.get('layers', []))}")
        lines.append(f"- **Highly Coupled Modules**: {len(assessment.get('coupled_modules', []))}")
        lines.append("")
        
        # Assessment
        lines.append("### Assessment\n")
        lines.append(f"{assessment.get('assessment', 'No assessment available')}\n")
        
        # Coupled modules
        coupled = assessment.get('coupled_modules', [])
        if coupled:
            lines.append("### Highly Coupled Modules\n")
            lines.append("The following modules exhibit high coupling and may benefit from refactoring:\n")
            for module in coupled:
                lines.append(f"- **{module}**")
            lines.append("")
        
        # Layers
        layers = assessment.get('layers', [])
        if layers:
            lines.append("### Architectural Layers\n")
            for i, layer in enumerate(layers, 1):
                lines.append(f"{i}. {layer}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_repository_health(self, health: Dict[str, Any]) -> str:
        """Format repository health section."""
        lines = ["## Repository Health\n"]
        
        if "status" in health:
            lines.append(f"*{health['status']}*\n")
            return "\n".join(lines)
        
        # Health scores table
        lines.append("| Dimension | Score | Status |")
        lines.append("|-----------|-------|--------|")
        
        arch_score = health.get('architecture_score', 0)
        lines.append(f"| Architecture | {arch_score}/10 | {self._get_score_badge(arch_score)} |")
        
        sec_score = health.get('security_score', 0)
        lines.append(f"| Security | {sec_score}/10 | {self._get_score_badge(sec_score)} |")
        
        qual_score = health.get('quality_score', 0)
        lines.append(f"| Code Quality | {qual_score}/10 | {self._get_score_badge(qual_score)} |")
        
        dep_score = health.get('dependency_score', 0)
        lines.append(f"| Dependencies | {dep_score}/10 | {self._get_score_badge(dep_score)} |")
        
        overall = health.get('overall_score', 0)
        lines.append(f"| **Overall** | **{overall:.1f}/10** | **{self._get_score_badge(overall)}** |")
        lines.append("")
        
        # Descriptions (without repeating scores)
        lines.append("### Architecture\n")
        lines.append(health.get('architecture_description', 'No description available'))
        lines.append("")
        
        lines.append("### Security\n")
        lines.append(health.get('security_description', 'No description available'))
        lines.append("")
        
        lines.append("### Code Quality\n")
        lines.append(health.get('quality_description', 'No description available'))
        lines.append("")
        
        lines.append("### Dependencies\n")
        lines.append(health.get('dependency_description', 'No description available'))
        lines.append("")
        
        # Risks
        risks = health.get('risks', [])
        if risks:
            lines.append("### Identified Risks\n")
            for risk in risks:
                lines.append(f"- ⚠️ {risk}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_security_findings(self, findings: Dict[str, Any]) -> str:
        """Format security findings section."""
        lines = ["## Security Findings\n"]
        
        if "status" in findings:
            lines.append(f"*{findings['status']}*\n")
            return "\n".join(lines)
        
        # Summary
        total = findings.get('total_issues', 0)
        risk = findings.get('risk_assessment', 'Unknown')
        lines.append(f"**Total Issues**: {total}")
        lines.append(f"**Risk Level**: {self._get_risk_badge(risk)}\n")
        
        # Severity breakdown
        severity = findings.get('severity_breakdown', {})
        if severity:
            lines.append("### Severity Breakdown\n")
            lines.append("| Severity | Count |")
            lines.append("|----------|-------|")
            for sev, count in severity.items():
                lines.append(f"| {sev.capitalize()} | {count} |")
            lines.append("")
        
        # Critical issues
        critical = findings.get('critical_issues', [])
        if critical:
            lines.append("### Critical Issues\n")
            for issue in critical[:3]:  # Top 3
                lines.append(f"- 🔴 **{issue.get('type', 'Unknown')}** in `{issue.get('file', 'Unknown')}`")
            lines.append("")
        
        # High issues
        high = findings.get('high_issues', [])
        if high:
            lines.append("### High Severity Issues\n")
            for issue in high[:5]:  # Top 5
                lines.append(f"- 🟠 **{issue.get('type', 'Unknown')}** in `{issue.get('file', 'Unknown')}`")
            lines.append("")
        
        # Affected files
        affected = findings.get('affected_files', [])
        if affected:
            lines.append("### Affected Files\n")
            for file in affected[:10]:  # Top 10
                lines.append(f"- `{file}`")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_timeline_activity(self, timeline: Dict[str, Any]) -> str:
        """Format timeline and recent activity section."""
        lines = ["## Timeline & Recent Activity\n"]
        
        if "status" in timeline:
            lines.append(f"*{timeline['status']}*\n")
            return "\n".join(lines)
        
        # Summary
        lines.append(timeline.get('activity_summary', 'No activity data available'))
        lines.append("")
        
        # Recent commits
        commits = timeline.get('recent_commits', [])
        if commits:
            lines.append("### Recent Commits\n")
            for commit in commits[:5]:  # Top 5
                if isinstance(commit, dict):
                    message = commit.get('message', 'No message')
                    author = commit.get('author', 'Unknown')
                    lines.append(f"- **{message[:60]}...** by {author}")
            lines.append("")
        
        # Files changed
        files = timeline.get('files_changed', [])
        if files:
            lines.append("### Files Changed\n")
            for file in files[:10]:  # Top 10
                lines.append(f"- `{file}`")
            lines.append("")
        
        # Affected subsystems
        subsystems = timeline.get('affected_subsystems', [])
        if subsystems:
            lines.append("### Affected Subsystems\n")
            for sub in subsystems[:5]:  # Top 5
                lines.append(f"- {sub}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_highest_risk_areas(self, risk_areas: List[Dict[str, Any]]) -> str:
        """Format highest risk areas section."""
        lines = ["## Highest Risk Areas\n"]
        
        if not risk_areas:
            lines.append("*No high-risk areas identified*\n")
            return "\n".join(lines)
        
        lines.append("| Area | Type | Severity | Impact |")
        lines.append("|------|------|----------|--------|")
        
        for area in risk_areas[:5]:  # Top 5
            area_name = area.get('area', 'Unknown')
            area_type = area.get('type', 'Unknown')
            severity = self._get_severity_badge(area.get('severity', 'medium'))
            impact = area.get('impact', 'Unknown')
            lines.append(f"| {area_name} | {area_type} | {severity} | {impact} |")
        
        lines.append("")
        return "\n".join(lines)
    
    def _format_recommended_actions(self, actions: List[Dict[str, Any]]) -> str:
        """Format recommended actions section."""
        lines = ["## Recommended Actions\n"]
        
        if not actions:
            lines.append("*No recommendations available*\n")
            return "\n".join(lines)
        
        lines.append("### Top Priority Actions\n")
        
        for i, action in enumerate(actions[:5], 1):  # Top 5
            priority = action.get('priority', 'Medium')
            action_text = action.get('action', 'No action specified')
            rationale = action.get('rationale', '')
            
            lines.append(f"#### {i}. {action_text}")
            lines.append(f"- **Priority**: {self._get_priority_badge(priority)}")
            lines.append(f"- **Rationale**: {rationale}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_suggested_refactoring(self, refactorings: List[Dict[str, Any]]) -> str:
        """Format suggested refactoring section."""
        lines = ["## Suggested Refactoring\n"]
        
        if not refactorings:
            lines.append("*No refactoring suggestions*\n")
            return "\n".join(lines)
        
        lines.append("| Target | Type | Description | Effort | Impact |")
        lines.append("|--------|------|-------------|--------|--------|")
        
        for refactoring in refactorings[:5]:  # Top 5
            target = refactoring.get('target', 'Unknown')
            ref_type = refactoring.get('type', 'Unknown')
            description = refactoring.get('description', 'No description')
            effort = refactoring.get('effort', 'Medium')
            impact = refactoring.get('impact', 'Medium')
            
            # Truncate description if too long
            if len(description) > 50:
                description = description[:47] + "..."
            
            lines.append(f"| {target} | {ref_type} | {description} | {effort} | {impact} |")
        
        lines.append("")
        return "\n".join(lines)
    
    def _format_overall_assessment(self, assessment: Dict[str, Any]) -> str:
        """Format overall assessment section."""
        lines = ["## Overall Engineering Assessment\n"]
        
        # Overall score
        score = assessment.get('overall_score', 0)
        lines.append(f"### Overall Score: {score:.1f}/10")
        lines.append(f"{self._get_score_badge(score)}\n")
        
        # Strengths
        strengths = assessment.get('strengths', [])
        if strengths:
            lines.append("### Strengths\n")
            for strength in strengths:
                lines.append(f"✓ {strength}")
            lines.append("")
        
        # Weaknesses
        weaknesses = assessment.get('weaknesses', [])
        if weaknesses:
            lines.append("### Areas for Improvement\n")
            for weakness in weaknesses:
                lines.append(f"• {weakness}")
            lines.append("")
        
        # Next steps
        next_steps = assessment.get('next_steps', [])
        if next_steps:
            lines.append("### Recommended Next Steps\n")
            for i, step in enumerate(next_steps, 1):
                lines.append(f"{i}. {step}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _get_score_badge(self, score: float) -> str:
        """Get a badge for a score."""
        if score >= 8:
            return "🟢 Excellent"
        elif score >= 6:
            return "🟡 Good"
        elif score >= 4:
            return "🟠 Fair"
        else:
            return "🔴 Poor"
    
    def _get_risk_badge(self, risk: str) -> str:
        """Get a badge for a risk level."""
        risk_lower = risk.lower()
        if "critical" in risk_lower:
            return "🔴 Critical"
        elif "high" in risk_lower:
            return "🟠 High"
        elif "medium" in risk_lower:
            return "🟡 Medium"
        else:
            return "🟢 Low"
    
    def _get_severity_badge(self, severity: str) -> str:
        """Get a badge for severity."""
        severity_lower = severity.lower()
        if severity_lower == "critical":
            return "🔴 Critical"
        elif severity_lower == "high":
            return "🟠 High"
        elif severity_lower == "medium":
            return "🟡 Medium"
        else:
            return "🟢 Low"
    
    def _get_priority_badge(self, priority: str) -> str:
        """Get a badge for priority."""
        priority_lower = priority.lower()
        if priority_lower == "critical":
            return "🔴 Critical"
        elif priority_lower == "high":
            return "🟠 High"
        else:
            return "🟡 Medium"
