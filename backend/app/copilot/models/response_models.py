"""Structured response models for Copilot.

These models represent the internal data structures used for response synthesis.
They are separate from presentation formatting.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum


class IntentType(Enum):
    """Enumeration of supported intent types."""
    ARCHITECTURE = "architecture"
    SECURITY = "security"
    METRICS = "metrics"
    TIMELINE = "timeline"
    HEALTH = "health"
    AUTHENTICATION = "authentication"
    GENERIC = "generic"


@dataclass
class ArchitectureData:
    """Structured data extracted from architecture analysis tools."""
    module_count: int = 0
    dependency_count: int = 0
    coupled_modules: List[str] = field(default_factory=list)
    modules: List[str] = field(default_factory=list)
    layers: List[str] = field(default_factory=list)
    
    def has_data(self) -> bool:
        """Check if this data object contains meaningful information."""
        return self.module_count > 0 or self.dependency_count > 0 or len(self.coupled_modules) > 0


@dataclass
class SecurityData:
    """Structured data extracted from security analysis tools."""
    total_issues: int = 0
    severity_breakdown: Dict[str, int] = field(default_factory=dict)
    critical_issues: List[Dict[str, str]] = field(default_factory=list)
    high_issues: List[Dict[str, str]] = field(default_factory=list)
    medium_issues: List[Dict[str, str]] = field(default_factory=list)
    low_issues: List[Dict[str, str]] = field(default_factory=list)
    affected_files: List[str] = field(default_factory=list)
    
    def has_data(self) -> bool:
        """Check if this data object contains meaningful information."""
        return self.total_issues > 0 or len(self.severity_breakdown) > 0


@dataclass
class MetricsData:
    """Structured data extracted from metrics analysis tools."""
    languages: List[tuple[str, int]] = field(default_factory=list)
    file_count: int = 0
    repo_size: str = ""
    frameworks: List[str] = field(default_factory=list)
    largest_directories: List[tuple[str, int]] = field(default_factory=list)
    
    def has_data(self) -> bool:
        """Check if this data object contains meaningful information."""
        return self.file_count > 0 or len(self.languages) > 0 or len(self.frameworks) > 0


@dataclass
class TimelineData:
    """Structured data extracted from timeline analysis tools."""
    recent_commits: List[Dict[str, str]] = field(default_factory=list)
    files_changed: List[str] = field(default_factory=list)
    affected_subsystems: List[str] = field(default_factory=list)
    commit_count: int = 0
    
    def has_data(self) -> bool:
        """Check if this data object contains meaningful information."""
        return self.commit_count > 0 or len(self.files_changed) > 0


@dataclass
class HealthData:
    """Structured data extracted from health analysis tools."""
    architecture_score: int = 8
    architecture_description: str = ""
    security_score: int = 8
    security_description: str = ""
    quality_score: int = 8
    quality_description: str = ""
    dependency_score: int = 8
    dependency_description: str = ""
    overall_score: float = 8.0
    risks: List[str] = field(default_factory=list)
    
    def has_data(self) -> bool:
        """Check if this data object contains meaningful information."""
        return any(score < 10 for score in [self.architecture_score, self.security_score, 
                                            self.quality_score, self.dependency_score])


@dataclass
class AuthenticationData:
    """Structured data extracted from authentication analysis tools."""
    components: List[str] = field(default_factory=list)
    flow_description: str = ""
    
    def has_data(self) -> bool:
        """Check if this data object contains meaningful information."""
        return len(self.components) > 0


@dataclass
class GenericData:
    """Structured data for generic/unrecognized intents."""
    summaries: List[str] = field(default_factory=list)
    key_findings: List[str] = field(default_factory=list)
    
    def has_data(self) -> bool:
        """Check if this data object contains meaningful information."""
        return len(self.summaries) > 0 or len(self.key_findings) > 0


@dataclass
class CopilotResponse:
    """Base response model containing all synthesized information."""
    intent: IntentType = IntentType.GENERIC
    architecture: Optional[ArchitectureData] = None
    security: Optional[SecurityData] = None
    metrics: Optional[MetricsData] = None
    timeline: Optional[TimelineData] = None
    health: Optional[HealthData] = None
    authentication: Optional[AuthenticationData] = None
    generic: Optional[GenericData] = None
    confidence: float = 0.7
    recommendations: List[str] = field(default_factory=list)
    raw_tool_data: Dict[str, Any] = field(default_factory=dict)
    
    def get_primary_data(self) -> Any:
        """Get the primary data object based on intent."""
        if self.intent == IntentType.ARCHITECTURE:
            return self.architecture
        elif self.intent == IntentType.SECURITY:
            return self.security
        elif self.intent == IntentType.METRICS:
            return self.metrics
        elif self.intent == IntentType.TIMELINE:
            return self.timeline
        elif self.intent == IntentType.HEALTH:
            return self.health
        elif self.intent == IntentType.AUTHENTICATION:
            return self.authentication
        else:
            return self.generic
