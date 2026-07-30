"""Response builder for Unified Intelligence Orchestrator (CG-070).

Builds structured engineering responses and keeps legacy helpers for
capability-routing compatibility.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ResponseBuilder:
    """Formats Copilot outputs into consistent API payloads."""

    def build_engineering_response(self, processed: Dict[str, Any], query: str, conversation_id: str) -> Dict[str, Any]:
        """Build the CG-070 structured engineering response."""
        return {
            "conversation_id": conversation_id,
            "query": query,
            "answer": processed.get("answer", ""),
            "confidence": processed.get("confidence", 0.0),
            "repository_context": processed.get("repository_context") or {},
            "modules_used": processed.get("modules_used") or [],
            "tools_used": processed.get("tools_used") or [],
            "reasoning_summary": processed.get("reasoning_summary", ""),
            "related_components": processed.get("related_components") or [],
            "related_files": processed.get("related_files") or [],
            "recommendations": processed.get("recommendations") or [],
            "follow_up_questions": processed.get("follow_up_questions") or [],
            "citations": processed.get("citations") or [],
            "execution_time_ms": processed.get("execution_time_ms", 0),
            "provider": processed.get("provider"),
            "intent": processed.get("intent"),
            "plan_confidence": processed.get("plan_confidence", 0.0),
        }

    def build_response(
        self,
        context: dict[str, Any],
        module_output: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Legacy builder used by IntentRouter path / older tests."""
        if module_output is None:
            return self._build_fallback_response(context)

        answer = self._extract_answer(module_output, context)
        sources = self._identify_sources(context)
        confidence = context.get("confidence", 70)
        evidence = self._gather_evidence(context, module_output)
        related_modules = self._identify_related_modules(context)

        return {
            "answer": answer,
            "sources": sources,
            "confidence": confidence,
            "evidence": evidence,
            "related_modules": related_modules,
        }

    def _build_fallback_response(self, context: dict[str, Any]) -> dict[str, Any]:
        repository_name = context.get("repository_name", "Unknown")
        health_score = context.get("health_score", 0)
        architecture_score = context.get("architecture_score", 0)

        answer = (
            f"Repository '{repository_name}'s current health score is {health_score}/100 "
            f"and architecture score is {architecture_score}/100."
        )
        if health_score >= 80 and architecture_score >= 80:
            answer += " Overall engineering health is strong."
        elif health_score < 60 or architecture_score < 60:
            answer += " Consider reviewing the architecture and implementing improvements."

        return {
            "answer": answer,
            "sources": ["Repository Registry"],
            "confidence": 60,
            "evidence": [
                f"Health Score: {health_score}",
                f"Architecture Score: {architecture_score}",
            ],
            "related_modules": ["Quality Analyzer", "Architecture Report"],
        }

    def _extract_answer(self, module_output: dict[str, Any], context: dict[str, Any]) -> str:
        intent = context.get("intent", "unknown")
        repository_name = context.get("repository_name", "Unknown")

        if intent == "repository_info":
            health_score = context.get("health_score", 0)
            architecture_score = context.get("architecture_score", 0)
            languages = context.get("languages", [])
            frameworks = context.get("frameworks", [])
            answer = (
                f"Repository '{repository_name}' has a health score of {health_score}/100 "
                f"and architecture score of {architecture_score}/100."
            )
            if languages:
                answer += f" It uses {', '.join(languages)}."
            if frameworks:
                answer += f" Frameworks include {', '.join(frameworks)}."
            return answer
        if intent == "architecture_health":
            architecture_score = context.get("architecture_score", 0)
            if architecture_score >= 80:
                return f"Repository '{repository_name}'s architecture is healthy with a score of {architecture_score}/100."
            if architecture_score >= 60:
                return (
                    f"Repository '{repository_name}'s architecture is satisfactory with a score of "
                    f"{architecture_score}/100, but has room for improvement."
                )
            return (
                f"Repository '{repository_name}'s architecture needs attention with a score of "
                f"{architecture_score}/100. Consider refactoring to improve modularity and separation of concerns."
            )
        if intent == "quality_analysis":
            quality_score = context.get("quality_score", 0)
            if quality_score >= 80:
                return f"Repository '{repository_name}'s code quality is strong with a score of {quality_score}/100."
            if quality_score >= 60:
                return (
                    f"Repository '{repository_name}'s code quality is moderate with a score of "
                    f"{quality_score}/100. Focus on improving test coverage and code maintainability."
                )
            return (
                f"Repository '{repository_name}'s code quality requires attention with a score of "
                f"{quality_score}/100. Consider refactoring and adding automated tests."
            )
        if intent == "security_analysis":
            security_score = context.get("security_score", 0)
            if security_score >= 80:
                return f"Repository '{repository_name}'s security posture is strong with a score of {security_score}/100."
            if security_score >= 60:
                return (
                    f"Repository '{repository_name}'s security posture is moderate with a score of "
                    f"{security_score}/100. Review dependencies and implement security best practices."
                )
            return (
                f"Repository '{repository_name}'s security posture needs attention with a score of "
                f"{security_score}/100. Address vulnerabilities and implement security measures."
            )
        if intent == "risk_analysis":
            risk_score = context.get("risk_score", 0)
            if risk_score < 30:
                return f"Repository '{repository_name}'s risk profile is low with a score of {risk_score}/100."
            if risk_score < 60:
                return (
                    f"Repository '{repository_name}'s risk profile is moderate with a score of "
                    f"{risk_score}/100. Monitor technical debt and high-risk areas."
                )
            return (
                f"Repository '{repository_name}'s risk profile is high with a score of "
                f"{risk_score}/100. Prioritize technical debt reduction and bug fixes."
            )
        if intent == "dependency_health":
            frameworks = context.get("frameworks", [])
            if frameworks:
                return (
                    f"Repository '{repository_name}'s uses {len(frameworks)} frameworks: "
                    f"{', '.join(frameworks)}. Monitor for vulnerabilities and keep dependencies updated."
                )
            return (
                f"Repository '{repository_name}'s dependency information is limited. "
                "Consider implementing dependency management best practices."
            )

        health_score = context.get("health_score", 0)
        architecture_score = context.get("architecture_score", 0)
        return (
            f"Repository '{repository_name}'s health score is {health_score}/100 and architecture score "
            f"is {architecture_score}/100. This provides a baseline for engineering quality assessment."
        )

    def _identify_sources(self, context: dict[str, Any]) -> list[str]:
        intent = context.get("intent", "unknown")
        sources = ["Repository Registry"]
        if intent == "architecture_health":
            sources.extend(["Architecture Report Engine", "Architecture Builder"])
        elif intent == "quality_analysis":
            sources.extend(["Quality Analyzer", "Code Metrics"])
        elif intent == "security_analysis":
            sources.extend(["Security Analyzer"])
        elif intent == "risk_analysis":
            sources.extend(["Risk Engine"])
        elif intent == "dependency_health":
            sources.extend(["Dependency Health Dashboard"])
        return list(set(sources))

    def _gather_evidence(
        self,
        context: dict[str, Any],
        module_output: dict[str, Any] | None,
    ) -> list[str]:
        evidence = [
            f"Repository: {context.get('repository_name', 'Unknown')}",
            f"Health Score: {context.get('health_score', 0)}/100",
            f"Architecture Score: {context.get('architecture_score', 0)}/100",
            f"Quality Score: {context.get('quality_score', 0)}/100",
            f"Security Score: {context.get('security_score', 0)}/100",
            f"Risk Score: {context.get('risk_score', 0)}/100",
        ]
        languages = context.get("languages", [])
        if languages:
            evidence.append(f"Languages: {', '.join(languages)}")
        frameworks = context.get("frameworks", [])
        if frameworks:
            evidence.append(f"Frameworks: {', '.join(frameworks)}")
        return evidence

    def _identify_related_modules(self, context: dict[str, Any]) -> list[str]:
        intent = context.get("intent", "unknown")
        related_modules = {
            "repository_info": ["Quality Analyzer", "Architecture Report"],
            "architecture_health": ["Architecture Report", "Architecture Recommendation", "Architecture Drift"],
            "quality_analysis": ["Quality Analyzer", "Code Metrics", "Risk Engine"],
            "security_analysis": ["Security Analyzer", "Dependency Health"],
            "risk_analysis": ["Risk Engine", "Quality Analyzer", "Architecture Report"],
            "dependency_health": ["Dependency Health", "Security Analyzer"],
            "bug_localization": ["Bug Localization", "Quality Analyzer"],
            "metrics": ["Metrics Dashboard", "Quality Analyzer"],
            "design_patterns": ["Design Patterns", "SOLID Analyzer"],
            "solid_principles": ["SOLID Analyzer", "Design Patterns"],
            "microservices": ["Microservice Detection", "Architecture Builder"],
            "database_schema": ["Database Schema", "API Flow"],
            "api_flow": ["API Flow", "API Documentation"],
            "documentation": ["README Generator", "API Documentation"],
            "uml_diagrams": ["UML Generator", "Architecture Builder"],
            "knowledge_graph": ["Knowledge Graph", "Repository Search"],
            "repository_comparison": ["Repository Comparison", "Team Analytics"],
            "release_notes": ["Release Notes Generator", "Team Analytics"],
            "dashboard": ["Executive Dashboard", "Team Analytics"],
            "team_analytics": ["Team Analytics", "Repository Comparison"],
            "cicd": ["CI/CD Integration", "GitHub Integration"],
            "github": ["GitHub Integration", "Repository Sync"],
            "jira": ["Jira Integration", "Notification Engine"],
        }
        return related_modules.get(intent, ["Quality Analyzer", "Architecture Report"])


response_builder = ResponseBuilder()
