"""Confidence calculation module.

Calculates confidence scores based on tool execution results.
"""

from typing import Dict, Any
from ..models.response_models import CopilotResponse


class ConfidenceCalculator:
    """Calculates confidence scores for copilot responses."""
    
    def calculate(self, tool_data: Dict[str, Any], response: CopilotResponse) -> float:
        """Calculate confidence based on tool execution results.
        
        Args:
            tool_data: Dictionary mapping tool names to their output data
            response: The copilot response object
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        tool_count = len(tool_data)
        if tool_count == 0:
            return 0.3
        
        # Check for data completeness
        has_data = sum(1 for data in tool_data.values() if data.get("data"))
        has_summary = sum(1 for data in tool_data.values() if data.get("summary"))
        
        # Base confidence from tool count
        confidence = min(0.5 + (tool_count * 0.1), 0.9)
        
        # Boost if tools have both summary and data
        if has_data == tool_count and has_summary == tool_count:
            confidence = min(confidence + 0.1, 0.95)
        
        # Reduce if tools are missing data
        if has_data < tool_count / 2:
            confidence -= 0.2
        
        # Adjust based on primary data availability
        primary_data = response.get_primary_data()
        if primary_data and hasattr(primary_data, 'has_data') and not primary_data.has_data():
            confidence -= 0.1
        
        return max(confidence, 0.4)
