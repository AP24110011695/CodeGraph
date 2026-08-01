"""Response synthesizer module.

Combines multiple extractor outputs into a unified response model.
"""

from typing import Dict, Any, List
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
from ..extractors.architecture import ArchitectureExtractor
from ..extractors.security import SecurityExtractor
from ..extractors.metrics import MetricsExtractor
from ..extractors.timeline import TimelineExtractor
from ..extractors.health import HealthExtractor
from ..extractors.authentication import AuthenticationExtractor
from .confidence import ConfidenceCalculator


class ResponseSynthesizer:
    """Synthesizes a unified response from multiple tool outputs."""
    
    def __init__(self) -> None:
        self.architecture_extractor = ArchitectureExtractor()
        self.security_extractor = SecurityExtractor()
        self.metrics_extractor = MetricsExtractor()
        self.timeline_extractor = TimelineExtractor()
        self.health_extractor = HealthExtractor()
        self.authentication_extractor = AuthenticationExtractor()
        self.confidence_calculator = ConfidenceCalculator()
    
    def synthesize(self, tool_data: Dict[str, Any], intent: str, question: str) -> CopilotResponse:
        """Synthesize a unified response from tool outputs.
        
        Args:
            tool_data: Dictionary mapping tool names to their output data
            intent: The detected intent (from IntentRouter)
            question: The original user question
            
        Returns:
            CopilotResponse object with synthesized data
        """
        if not tool_data:
            return CopilotResponse(intent=IntentType.GENERIC, confidence=0.1)
        
        # Map intent string to IntentType enum
        intent_type = self._map_intent(intent)
        
        # Create response object
        response = CopilotResponse(intent=intent_type, raw_tool_data=tool_data)
        
        # Extract data based on intent
        if intent_type == IntentType.ARCHITECTURE:
            response.architecture = self.architecture_extractor.extract(tool_data)
            response.recommendations = self._generate_architecture_recommendations(response.architecture)
        
        elif intent_type == IntentType.SECURITY:
            response.security = self.security_extractor.extract(tool_data)
            response.recommendations = self._generate_security_recommendations(response.security)
        
        elif intent_type == IntentType.METRICS:
            response.metrics = self.metrics_extractor.extract(tool_data)
            response.recommendations = self._generate_metrics_recommendations(response.metrics)
        
        elif intent_type == IntentType.TIMELINE:
            response.timeline = self.timeline_extractor.extract(tool_data)
            response.recommendations = self._generate_timeline_recommendations(response.timeline)
        
        elif intent_type == IntentType.HEALTH:
            response.health = self.health_extractor.extract(tool_data)
            response.recommendations = self._generate_health_recommendations(response.health)
        
        elif intent_type == IntentType.AUTHENTICATION:
            response.authentication = self.authentication_extractor.extract(tool_data)
            response.recommendations = self._generate_authentication_recommendations(response.authentication)
        
        else:
            # Generic intent - extract all available data
            response.architecture = self.architecture_extractor.extract(tool_data)
            response.security = self.security_extractor.extract(tool_data)
            response.metrics = self.metrics_extractor.extract(tool_data)
            response.recommendations = self._generate_generic_recommendations()
        
        # Calculate confidence
        response.confidence = self.confidence_calculator.calculate(tool_data, response)
        
        return response
    
    def _map_intent(self, intent: str) -> IntentType:
        """Map intent string to IntentType enum."""
        intent_lower = intent.lower()
        
        # Check for compound intents first (more specific)
        if "architecture" in intent_lower:
            return IntentType.ARCHITECTURE
        elif "security" in intent_lower:
            return IntentType.SECURITY
        elif "authentication" in intent_lower or "auth" in intent_lower:
            return IntentType.AUTHENTICATION
        elif "timeline" in intent_lower or "recent" in intent_lower or "change" in intent_lower:
            return IntentType.TIMELINE
        elif "language" in intent_lower or "metric" in intent_lower or "framework" in intent_lower:
            return IntentType.METRICS
        elif "health" in intent_lower or "report" in intent_lower or "overall" in intent_lower or "assessment" in intent_lower:
            return IntentType.HEALTH
        elif intent_lower in ["structure", "design", "layer"]:
            return IntentType.ARCHITECTURE
        elif intent_lower in ["vulnerability", "risk", "threat", "cve"]:
            return IntentType.SECURITY
        elif intent_lower in ["programming", "tech stack", "size"]:
            return IntentType.METRICS
        elif intent_lower in ["commit", "history", "activity"]:
            return IntentType.TIMELINE
        else:
            return IntentType.GENERIC
    
    def _generate_architecture_recommendations(self, arch_data: ArchitectureData) -> List[str]:
        """Generate architecture-specific recommendations."""
        recommendations: List[str] = []
        
        if arch_data.coupled_modules:
            recommendations.append("Review the dependency graph to identify refactoring opportunities in highly coupled modules")
        
        if arch_data.layers:
            recommendations.append("Verify that dependencies flow only downward between layers")
        
        recommendations.append("Analyze the authentication flow to ensure security boundaries are properly defined")
        recommendations.append("Consider introducing event-driven communication for cross-cutting concerns")
        
        return recommendations
    
    def _generate_security_recommendations(self, sec_data: SecurityData) -> List[str]:
        """Generate security-specific recommendations."""
        recommendations: List[str] = []
        
        if sec_data.critical_issues or sec_data.high_issues:
            recommendations.append("Review and patch all critical and high-severity vulnerabilities")
            recommendations.append("Update dependencies to their latest secure versions")
            recommendations.append("Implement input validation and output encoding")
            recommendations.append("Add security headers to HTTP responses")
        
        recommendations.append("Integrate automated security scanning into CI/CD pipeline")
        recommendations.append("Establish regular dependency update procedures")
        recommendations.append("Conduct periodic security audits and penetration testing")
        recommendations.append("Implement security training for development team")
        
        return recommendations
    
    def _generate_metrics_recommendations(self, metrics_data: MetricsData) -> List[str]:
        """Generate metrics-specific recommendations."""
        recommendations: List[str] = []
        
        if metrics_data.file_count > 1000:
            recommendations.append("Consider modularizing the codebase to improve maintainability")
        
        if len(metrics_data.languages) > 3:
            recommendations.append("Evaluate whether the polyglot architecture is necessary or can be simplified")
        
        recommendations.append("Review the largest directories for potential refactoring opportunities")
        recommendations.append("Ensure consistent coding standards across all languages used")
        
        return recommendations
    
    def _generate_timeline_recommendations(self, timeline_data: TimelineData) -> List[str]:
        """Generate timeline-specific recommendations."""
        return [
            "Review the impact analysis to understand affected components",
            "Compare with previous version to identify unintended changes",
            "Run comprehensive tests on affected subsystems",
            "Update documentation to reflect recent changes"
        ]
    
    def _generate_health_recommendations(self, health_data: HealthData) -> List[str]:
        """Generate health-specific recommendations."""
        return [
            "Review critical issues identified in this report",
            "Generate a detailed PDF report for stakeholders",
            "Schedule regular health assessments",
            "Address items with scores below 6/10"
        ]
    
    def _generate_authentication_recommendations(self, auth_data: AuthenticationData) -> List[str]:
        """Generate authentication-specific recommendations."""
        return [
            "Review the dependency graph to understand authentication dependencies",
            "Verify that security boundaries are properly defined",
            "Ensure proper error handling for authentication failures",
            "Consider implementing multi-factor authentication"
        ]
    
    def _generate_generic_recommendations(self) -> List[str]:
        """Generate generic recommendations."""
        return [
            "Review the detailed analysis for more information",
            "Consider exploring related aspects of the repository",
            "Use the dependency graph to understand component relationships"
        ]
