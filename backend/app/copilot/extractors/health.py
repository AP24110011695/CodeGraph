"""Health data extractor.

Extracts structured health information from tool outputs.
"""

from typing import Dict, Any, List
from .architecture import ArchitectureExtractor
from .security import SecurityExtractor
from .metrics import MetricsExtractor
from ..models.response_models import HealthData, ArchitectureData, SecurityData, MetricsData


class HealthExtractor:
    """Extracts health-related data from tool outputs."""
    
    def __init__(self):
        self.architecture_extractor = ArchitectureExtractor()
        self.security_extractor = SecurityExtractor()
        self.metrics_extractor = MetricsExtractor()
    
    def extract(self, tool_data: Dict[str, Any]) -> HealthData:
        """Extract health data from tool outputs.
        
        Args:
            tool_data: Dictionary mapping tool names to their output data
            
        Returns:
            HealthData object with extracted information
        """
        if not tool_data:
            return HealthData()
        
        data = HealthData()
        
        # Extract data from individual extractors
        arch_data = self.architecture_extractor.extract(tool_data)
        sec_data = self.security_extractor.extract(tool_data)
        metrics_data = self.metrics_extractor.extract(tool_data)
        
        # Assess architecture health
        data.architecture_score = self._assess_architecture_score(arch_data)
        data.architecture_description = self._assess_architecture_description(arch_data, data.architecture_score)
        
        # Assess security health
        data.security_score = self._assess_security_score(sec_data)
        data.security_description = self._assess_security_description(sec_data, data.security_score)
        
        # Assess quality health
        data.quality_score = self._assess_quality_score(metrics_data)
        data.quality_description = self._assess_quality_description(metrics_data, data.quality_score)
        
        # Assess dependency health
        data.dependency_score = self._assess_dependency_score(arch_data)
        data.dependency_description = self._assess_dependency_description(arch_data, data.dependency_score)
        
        # Calculate overall score
        data.overall_score = (data.architecture_score + data.security_score + 
                            data.quality_score + data.dependency_score) / 4
        
        # Identify risks
        data.risks = self._identify_risks(data)
        
        return data
    
    def _assess_architecture_score(self, arch_data: ArchitectureData) -> int:
        """Calculate architecture health score."""
        score = 8  # Base score
        if len(arch_data.coupled_modules) > 5:
            score -= 2
        if arch_data.module_count > 100:
            score -= 1
        return max(score, 1)
    
    def _assess_architecture_description(self, arch_data: ArchitectureData, score: int) -> str:
        """Generate architecture health description."""
        description = f"The repository has {arch_data.module_count} modules with {len(arch_data.coupled_modules)} highly coupled components. "
        if score >= 7:
            description += "Architecture is well-structured with manageable complexity."
        elif score >= 5:
            description += "Architecture shows some complexity that may impact maintainability."
        else:
            description += "Architecture requires attention to reduce coupling and improve modularity."
        return description
    
    def _assess_security_score(self, sec_data: SecurityData) -> int:
        """Calculate security health score."""
        total = sec_data.total_issues
        score = 10 - min(total, 5)  # Deduct up to 5 points for issues
        return max(score, 1)
    
    def _assess_security_description(self, sec_data: SecurityData, score: int) -> str:
        """Generate security health description."""
        total = sec_data.total_issues
        description = f"Found {total} security issue(s). "
        if score >= 8:
            description += "Security posture is strong with minimal vulnerabilities."
        elif score >= 5:
            description += "Security posture is acceptable with room for improvement."
        else:
            description += "Security posture requires immediate attention."
        return description
    
    def _assess_quality_score(self, metrics_data: MetricsData) -> int:
        """Calculate quality health score."""
        file_count = metrics_data.file_count
        score = 7  # Base score
        if file_count > 1000:
            score -= 1
        return max(score, 1)
    
    def _assess_quality_description(self, metrics_data: MetricsData, score: int) -> str:
        """Generate quality health description."""
        file_count = metrics_data.file_count
        description = f"Repository contains {file_count} files. "
        if score >= 7:
            description += "Code quality appears good based on available metrics."
        else:
            description += "Code quality may benefit from additional analysis and refactoring."
        return description
    
    def _assess_dependency_score(self, arch_data: ArchitectureData) -> int:
        """Calculate dependency health score."""
        deps = arch_data.dependency_count
        score = 8  # Base score
        if deps > 500:
            score -= 2
        elif deps > 200:
            score -= 1
        return max(score, 1)
    
    def _assess_dependency_description(self, arch_data: ArchitectureData, score: int) -> str:
        """Generate dependency health description."""
        deps = arch_data.dependency_count
        description = f"Repository has {deps} dependencies. "
        if score >= 7:
            description += "Dependency structure is manageable."
        else:
            description += "Dependency complexity may require attention."
        return description
    
    def _identify_risks(self, health_data: HealthData) -> List[str]:
        """Identify risks based on health scores."""
        risks: List[str] = []
        if health_data.architecture_score < 6:
            risks.append("Architecture complexity may impact maintainability")
        if health_data.security_score < 6:
            risks.append("Security vulnerabilities require immediate attention")
        if health_data.dependency_score < 6:
            risks.append("Dependency issues may affect stability")
        return risks
