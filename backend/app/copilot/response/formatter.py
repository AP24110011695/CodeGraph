"""Response formatter module.

Formats structured response data into presentation formats.
Currently supports Markdown formatting, designed to be extensible for HTML/PDF/JSON.
"""

from abc import ABC, abstractmethod
from typing import Any, List, Optional
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


class ResponseFormatter(ABC):
    """Abstract base class for response formatters."""
    
    @abstractmethod
    def format(self, response: CopilotResponse, question: str) -> str:
        """Format a copilot response into a presentation format.
        
        Args:
            response: The copilot response object with structured data
            question: The original user question
            
        Returns:
            Formatted response string
        """
        pass


class MarkdownFormatter(ResponseFormatter):
    """Formats copilot responses as Markdown."""
    
    def format(self, response: CopilotResponse, question: str) -> str:
        """Format a copilot response as Markdown.
        
        Args:
            response: The copilot response object with structured data
            question: The original user question
            
        Returns:
            Markdown-formatted response string
        """
        intent = response.intent
        
        if intent == IntentType.ARCHITECTURE:
            return self._format_architecture(response.architecture, response.recommendations)
        elif intent == IntentType.SECURITY:
            return self._format_security(response.security, response.recommendations)
        elif intent == IntentType.METRICS:
            return self._format_metrics(response.metrics, response.recommendations)
        elif intent == IntentType.TIMELINE:
            return self._format_timeline(response.timeline, response.recommendations)
        elif intent == IntentType.HEALTH:
            return self._format_health(response.health, response.recommendations)
        elif intent == IntentType.AUTHENTICATION:
            return self._format_authentication(response.authentication, response.recommendations)
        else:
            return self._format_generic(response, question)
    
    def _format_architecture(self, arch_data: Optional[ArchitectureData], recommendations: List[str]) -> str:
        """Format architecture data as Markdown."""
        report = ["# Repository Architecture\n"]
        
        if not arch_data:
            report.append("Architecture data not available.\n")
            return "\n".join(report)
        
        # Overview
        report.append("## Overview\n")
        if arch_data.module_count > 0:
            report.append(f"The repository is organized into **{arch_data.module_count} modules**")
            if arch_data.layers:
                report.append(f" across **{len(arch_data.layers)} distinct layers**")
            report.append(". ")
        
        if arch_data.dependency_count > 0:
            report.append(f"These modules are connected through **{arch_data.dependency_count} relationships**. ")
        
        # Add architectural insight
        if arch_data.layers and len(arch_data.layers) > 1:
            report.append(f"The codebase follows a **layered architecture** pattern, with clear separation between {', '.join(arch_data.layers[:3])}. ")
            report.append("This structure promotes maintainability by isolating concerns and controlling dependencies between layers.\n")
        elif arch_data.module_count > 0:
            report.append("The architecture appears to be **modular**, with components organized by functional responsibility. ")
            report.append("This approach supports parallel development and testing, though care should be taken to manage inter-module dependencies.\n")
        
        # Layers
        if arch_data.layers:
            report.append("## Layers\n")
            for i, layer in enumerate(arch_data.layers, 1):
                report.append(f"**{i}. {layer}**")
                if i == 1:
                    report.append(" - Handles user interaction and presentation logic")
                elif i == len(arch_data.layers):
                    report.append(" - Manages data persistence and external integrations")
                else:
                    report.append(" - Contains core business logic and domain services")
            report.append("")
        
        # Main modules
        if arch_data.modules and len(arch_data.modules) > 0:
            report.append("## Main Modules\n")
            for module in arch_data.modules[:8]:
                report.append(f"- **{module}**")
            if len(arch_data.modules) > 8:
                report.append(f"- ... and {len(arch_data.modules) - 8} more modules")
            report.append("")
        
        # How they interact
        if arch_data.dependency_count > 0:
            report.append("## Module Interactions\n")
            report.append(f"The repository contains **{arch_data.dependency_count} dependency relationships** between modules. ")
            if arch_data.coupled_modules:
                report.append(f"**{len(arch_data.coupled_modules)} modules** exhibit high coupling, indicating concentrated dependencies that may impact maintainability. ")
            report.append("Most communication flows through the service layer, suggesting a centralized architecture pattern.\n")
        
        # Coupling analysis
        if arch_data.coupled_modules:
            report.append("## Coupling Analysis\n")
            report.append("The following modules have the highest coupling:")
            for module in arch_data.coupled_modules[:5]:
                report.append(f"- **{module}**")
            report.append("")
            report.append("**High coupling** can make the codebase harder to modify and test. Consider these improvements:")
            report.append("- Extract shared functionality into separate services")
            report.append("- Introduce interfaces to decouple implementations")
            report.append("- Apply dependency injection to reduce direct dependencies")
            report.append("")
        
        # Recommendations
        if recommendations:
            report.append("## Recommendations\n")
            for rec in recommendations:
                report.append(f"- {rec}")
            report.append("")
        
        # Summary
        report.append("## Summary\n")
        if arch_data.module_count > 0:
            report.append(f"This is a **{arch_data.module_count}-module repository")
            if arch_data.layers:
                report.append(f" organized into **{len(arch_data.layers)} architectural layers**")
            report.append(". ")
        
        if arch_data.coupled_modules:
            report.append(f"The presence of **{len(arch_data.coupled_modules)} highly coupled modules** suggests opportunities for architectural refinement. ")
        
        return "\n".join(report)
    
    def _format_security(self, sec_data: Optional[SecurityData], recommendations: List[str]) -> str:
        """Format security data as Markdown."""
        report = ["# Security Assessment\n"]
        
        if not sec_data:
            report.append("Security data not available.\n")
            return "\n".join(report)
        
        # Overall security posture
        report.append("## Overall Security Posture\n")
        if sec_data.total_issues == 0:
            report.append("**No security vulnerabilities were detected** in the repository. ")
            report.append("The codebase appears to follow security best practices. ")
            report.append("However, this analysis is based on automated scanning and should be complemented with manual security reviews.\n")
        elif sec_data.total_issues <= 5:
            report.append(f"The repository has **{sec_data.total_issues} security issue(s)**, indicating a **moderate security posture**. ")
            report.append("While the number of issues is low, each should be reviewed and addressed to prevent potential exploits.\n")
        elif sec_data.total_issues <= 15:
            report.append(f"The repository has **{sec_data.total_issues} security issue(s)**, indicating a **needs improvement** security posture. ")
            report.append("Prioritizing remediation of critical and high-severity issues is recommended.\n")
        else:
            report.append(f"The repository has **{sec_data.total_issues} security issue(s)**, indicating a **concerning security posture**. ")
            report.append("A comprehensive security audit and remediation plan is strongly recommended.\n")
        
        # Severity breakdown
        if sec_data.severity_breakdown:
            report.append("## Severity Breakdown\n")
            severity_order = ["critical", "high", "medium", "low"]
            for severity in severity_order:
                if severity in sec_data.severity_breakdown:
                    count = sec_data.severity_breakdown[severity]
                    if count > 0:
                        icon = "🔴" if severity == "critical" else "🟠" if severity == "high" else "🟡" if severity == "medium" else "🟢"
                        report.append(f"- {icon} **{severity.capitalize()}**: {count} issue(s)")
            report.append("")
        
        # Critical findings
        if sec_data.critical_issues:
            report.append("## Critical Findings\n")
            for issue in sec_data.critical_issues[:5]:
                vuln_type = issue.get("type", "Unknown")
                file_path = issue.get("file", "Unknown location")
                report.append(f"- **{vuln_type}** in `{file_path}`")
                report.append("  - Requires immediate attention as this could lead to system compromise")
            report.append("")
        
        # High findings
        if sec_data.high_issues:
            report.append("## High Severity Findings\n")
            for issue in sec_data.high_issues[:5]:
                vuln_type = issue.get("type", "Unknown")
                file_path = issue.get("file", "Unknown location")
                report.append(f"- **{vuln_type}** in `{file_path}`")
            report.append("")
        
        # Medium findings
        if sec_data.medium_issues:
            report.append("## Medium Severity Findings\n")
            report.append(f"Found **{len(sec_data.medium_issues)} medium-severity issues** that should be addressed as part of regular maintenance. ")
            report.append("These issues are less likely to be exploited but could impact security hygiene.\n")
        
        # Files involved
        if sec_data.affected_files:
            report.append("## Files Involved\n")
            report.append(f"**{len(sec_data.affected_files)} file(s)** are affected by security issues:")
            for file_path in sec_data.affected_files[:10]:
                report.append(f"- `{file_path}`")
            if len(sec_data.affected_files) > 10:
                report.append(f"- ... and {len(sec_data.affected_files) - 10} more files")
            report.append("")
        
        # Recommended fixes
        if recommendations:
            report.append("## Recommended Fixes\n")
            if sec_data.critical_issues or sec_data.high_issues:
                report.append("**Immediate Actions:**")
                for rec in recommendations[:4]:
                    report.append(f"- {rec}")
                report.append("")
                report.append("**Long-term Improvements:**")
                for rec in recommendations[4:]:
                    report.append(f"- {rec}")
            else:
                for rec in recommendations:
                    report.append(f"- {rec}")
            report.append("")
        
        # Overall risk
        report.append("## Overall Risk\n")
        if sec_data.total_issues == 0:
            report.append("**Risk Level: Low**")
        elif sec_data.total_issues <= 5:
            report.append("**Risk Level: Medium**")
        elif sec_data.total_issues <= 15:
            report.append("**Risk Level: High**")
        else:
            report.append("**Risk Level: Critical**")
        
        return "\n".join(report)
    
    def _format_metrics(self, metrics_data: Optional[MetricsData], recommendations: List[str]) -> str:
        """Format metrics data as Markdown."""
        report = ["# Repository Metrics\n"]
        
        if not metrics_data:
            report.append("Metrics data not available.\n")
            return "\n".join(report)
        
        # Languages
        report.append("## Languages\n")
        if metrics_data.languages:
            total_files = sum(count for _, count in metrics_data.languages)
            report.append(f"The codebase uses **{len(metrics_data.languages)} programming language(s)** across **{total_files} files**:")
            for lang, count in sorted(metrics_data.languages, key=lambda x: x[1], reverse=True):
                percentage = (count / total_files * 100) if total_files > 0 else 0
                report.append(f"- **{lang}**: {count} files ({percentage:.1f}%)")
            
            dominant = max(metrics_data.languages, key=lambda x: x[1])
            report.append(f"\n**{dominant[0]}** is the dominant language, comprising {(dominant[1] / total_files * 100):.1f}% of the codebase. ")
            report.append("This suggests the repository is primarily focused on this technology stack.\n")
        else:
            report.append("Language information is not available in the current analysis.\n")
        
        # Frameworks
        if metrics_data.frameworks:
            report.append("## Frameworks\n")
            report.append("The following frameworks and libraries are detected:")
            for framework in metrics_data.frameworks:
                report.append(f"- **{framework}**")
            report.append("")
        
        # Repository size
        report.append("## Repository Size\n")
        if metrics_data.file_count > 0:
            report.append(f"The repository contains **{metrics_data.file_count} files**. ")
            if metrics_data.file_count < 100:
                report.append("This is a **small repository** suitable for rapid development and iteration.\n")
            elif metrics_data.file_count < 500:
                report.append("This is a **medium-sized repository** with a balanced scope and complexity.\n")
            elif metrics_data.file_count < 2000:
                report.append("This is a **large repository** requiring careful architectural planning and team coordination.\n")
            else:
                report.append("This is an **enterprise-scale repository** with significant complexity and maintenance requirements.\n")
        
        if metrics_data.repo_size:
            report.append(f"Total repository size is approximately **{metrics_data.repo_size}**. ")
            report.append("This includes source code, configuration files, documentation, and build artifacts.\n")
        
        # Largest directories
        if metrics_data.largest_directories:
            report.append("## Largest Directories\n")
            report.append("The following directories contain the most files:")
            for dir_name, count in metrics_data.largest_directories[:5]:
                report.append(f"- **{dir_name}**: {count} files")
            report.append("")
        
        # Interesting observations
        report.append("## Interesting Observations\n")
        observations = []
        
        if metrics_data.languages:
            if len(metrics_data.languages) > 3:
                observations.append(f"The codebase uses **{len(metrics_data.languages)} different languages**, indicating a polyglot architecture. This provides flexibility but may increase build and deployment complexity.")
            elif len(metrics_data.languages) == 1:
                observations.append(f"The repository is **monolingual**, using only {metrics_data.languages[0][0]}. This simplifies the development environment but may limit future technology choices.")
        
        if metrics_data.file_count > 0:
            if metrics_data.file_count > 1000:
                observations.append(f"With **{metrics_data.file_count} files**, the repository would benefit from modularization and clear architectural boundaries to maintain developer productivity.")
        
        if not observations:
            observations.append("The repository follows standard project structure with no unusual patterns detected.")
        
        for obs in observations:
            report.append(f"- {obs}")
        report.append("")
        
        # Recommendations
        if recommendations:
            report.append("## Recommendations\n")
            for rec in recommendations:
                report.append(f"- {rec}")
        
        return "\n".join(report)
    
    def _format_timeline(self, timeline_data: Optional[TimelineData], recommendations: List[str]) -> str:
        """Format timeline data as Markdown."""
        report = ["# Recent Repository Activity\n"]
        
        if not timeline_data:
            report.append("Timeline data not available.\n")
            return "\n".join(report)
        
        # Recent commits
        report.append("## Recent Commits\n")
        if timeline_data.recent_commits:
            report.append(f"Found **{len(timeline_data.recent_commits)} recent commit(s)**:")
            for commit in timeline_data.recent_commits[:5]:
                if isinstance(commit, dict):
                    message = commit.get("message", "No message")
                    author = commit.get("author", "Unknown")
                    report.append(f"- **{message[:60]}...** by {author}")
            if len(timeline_data.recent_commits) > 5:
                report.append(f"- ... and {len(timeline_data.recent_commits) - 5} more commits")
            report.append("")
        else:
            report.append("Recent commit information is not available in the current analysis.\n")
        
        # Files changed
        if timeline_data.files_changed:
            report.append("## Files Changed\n")
            report.append(f"**{len(timeline_data.files_changed)} file(s)** were modified recently:")
            for file_path in timeline_data.files_changed[:10]:
                report.append(f"- `{file_path}`")
            if len(timeline_data.files_changed) > 10:
                report.append(f"- ... and {len(timeline_data.files_changed) - 10} more files")
            report.append("")
        
        # Subsystems affected
        if timeline_data.affected_subsystems:
            report.append("## Subsystems Affected\n")
            report.append("The following subsystems were impacted by recent changes:")
            for subsystem in timeline_data.affected_subsystems:
                report.append(f"- **{subsystem}**")
            report.append("")
        
        # Engineering impact
        report.append("## Engineering Impact\n")
        if timeline_data.files_changed:
            if len(timeline_data.files_changed) < 10:
                report.append("The recent changes are **focused and targeted**, suggesting a well-planned development approach. ")
                report.append("This minimizes regression risk and makes code review more manageable.\n")
            elif len(timeline_data.files_changed) < 50:
                report.append("The recent changes represent a **moderate scope** of work. ")
                report.append("Ensure comprehensive testing is performed to validate the changes.\n")
            else:
                report.append("The recent changes represent a **significant scope** of work. ")
                report.append("Consider breaking down large changes into smaller, incremental updates to reduce risk.\n")
        
        # Recommendations
        if recommendations:
            report.append("## Recommendations\n")
            for rec in recommendations:
                report.append(f"- {rec}")
        
        return "\n".join(report)
    
    def _format_health(self, health_data: Optional[HealthData], recommendations: List[str]) -> str:
        """Format health data as Markdown."""
        report = ["# Repository Health Report\n"]
        
        if not health_data:
            report.append("Health data not available.\n")
            return "\n".join(report)
        
        # Architecture section
        report.append("## Architecture\n")
        report.append(health_data.architecture_description)
        report.append(f"**Score: {health_data.architecture_score}/10**\n")
        
        # Security section
        report.append("## Security\n")
        report.append(health_data.security_description)
        report.append(f"**Score: {health_data.security_score}/10**\n")
        
        # Quality section
        report.append("## Code Quality\n")
        report.append(health_data.quality_description)
        report.append(f"**Score: {health_data.quality_score}/10**\n")
        
        # Dependencies section
        report.append("## Dependencies\n")
        report.append(health_data.dependency_description)
        report.append(f"**Score: {health_data.dependency_score}/10**\n")
        
        # Risks
        report.append("## Risks\n")
        if health_data.risks:
            for risk in health_data.risks:
                report.append(risk)
        else:
            report.append("No critical risks identified at this time.")
        report.append("")
        
        # Recommendations
        if recommendations:
            report.append("## Recommendations\n")
            for rec in recommendations:
                report.append(f"- {rec}")
            report.append("")
        
        # Overall score
        report.append("## Overall Score\n")
        report.append(f"**{health_data.overall_score:.1f}/10**")
        
        return "\n".join(report)
    
    def _format_authentication(self, auth_data: Optional[AuthenticationData], recommendations: List[str]) -> str:
        """Format authentication data as Markdown."""
        report = ["# Authentication Flow\n"]
        
        if not auth_data:
            report.append("Authentication data not available.\n")
            return "\n".join(report)
        
        # Overview
        report.append("## Overview\n")
        if auth_data.components:
            report.append(f"The authentication system involves **{len(auth_data.components)} components**. ")
            report.append("These components work together to secure user access and protect sensitive resources.\n")
        else:
            report.append("Authentication component information is not available in the current analysis. ")
            report.append("This may indicate that authentication is handled externally or through third-party services.\n")
        
        # Components
        if auth_data.components:
            report.append("## Components\n")
            for component in auth_data.components:
                report.append(f"- **{component}**")
            report.append("")
        
        # Flow
        if auth_data.flow_description:
            report.append("## Flow\n")
            report.append(auth_data.flow_description)
            report.append("")
        
        # Recommendations
        if recommendations:
            report.append("## Recommendations\n")
            for rec in recommendations:
                report.append(f"- {rec}")
        
        return "\n".join(report)
    
    def _format_generic(self, response: CopilotResponse, question: str) -> str:
        """Format generic response as Markdown."""
        report = [f"# Analysis Results\n"]
        report.append(f'Based on the analysis of your question about "{question}":\n')
        
        # Merge all tool outputs into a coherent summary
        all_summaries = []
        for tool_name, data in response.raw_tool_data.items():
            if data.get("summary"):
                summary = data["summary"]
                # Clean up common prefixes
                for prefix in ["Repository metrics:", "Dependency graph:", "Security analysis found", "Architecture:", "Timeline:"]:
                    if summary.startswith(prefix):
                        summary = summary[len(prefix):].strip()
                all_summaries.append(summary)
        
        if all_summaries:
            report.append("## Key Findings\n")
            for summary in all_summaries:
                report.append(f"- {summary}")
            report.append("")
        
        # Recommendations
        if response.recommendations:
            report.append("## Recommendations\n")
            for rec in response.recommendations:
                report.append(f"- {rec}")
        
        if not all_summaries and not response.recommendations:
            report.append("I could not find enough analyzed repository information to answer this question.\n")
        
        return "\n".join(report)
