"""Security data extractor.

Extracts structured security information from tool outputs.
"""

from typing import Dict, Any, List
from ..models.response_models import SecurityData
from .parsing_utils import ParsingUtils


class SecurityExtractor:
    """Extracts security-related data from tool outputs."""
    
    def extract(self, tool_data: Dict[str, Any]) -> SecurityData:
        """Extract security data from tool outputs.
        
        Args:
            tool_data: Dictionary mapping tool names to their output data
            
        Returns:
            SecurityData object with extracted information
        """
        if not tool_data:
            return SecurityData()
        
        data = SecurityData()
        
        for tool_name, tool_output in tool_data.items():
            data_str = tool_output.get("data", "")
            summary_str = tool_output.get("summary", "")
            
            # Extract total issues
            total_match = ParsingUtils.extract_count(summary_str, [r'(\d+)\s*issue'])
            data.total_issues += total_match
            
            # Extract severity breakdown
            severity_data = self._extract_severity_breakdown(data_str)
            for severity, count in severity_data.items():
                data.severity_breakdown[severity] = data.severity_breakdown.get(severity, 0) + count
            
            # Extract specific issues
            issues = self._extract_specific_issues(data_str)
            for issue in issues:
                severity = issue.get("severity", "").lower()
                if severity == "critical":
                    data.critical_issues.append(issue)
                elif severity == "high":
                    data.high_issues.append(issue)
                elif severity == "medium":
                    data.medium_issues.append(issue)
                elif severity == "low":
                    data.low_issues.append(issue)
            
            # Extract affected files
            for issue in issues:
                file_path = issue.get("file")
                if file_path and file_path not in data.affected_files:
                    data.affected_files.append(file_path)
        
        return data
    
    def _extract_severity_breakdown(self, data_str: str) -> Dict[str, int]:
        """Extract severity breakdown from tool data."""
        breakdown = {}
        
        # Try to find the summary dict specifically
        summary_dict = ParsingUtils.extract_dict(data_str, "summary")
        if summary_dict:
            for severity, count in summary_dict.items():
                if isinstance(count, (int, float)):
                    breakdown[severity.lower()] = int(count)
        else:
            # Fallback: try to find any dict that looks like a severity breakdown
            generic_dict = ParsingUtils.extract_dict(data_str)
            if generic_dict and any(k.lower() in ['critical', 'high', 'medium', 'low'] for k in generic_dict.keys()):
                for severity, count in generic_dict.items():
                    if isinstance(count, (int, float)):
                        breakdown[severity.lower()] = int(count)
        
        return breakdown
    
    def _extract_specific_issues(self, data_str: str) -> List[Dict[str, str]]:
        """Extract specific security issues from tool data."""
        if "issues" not in data_str:
            return []
        
        issues_list = ParsingUtils.extract_list(data_str)
        if isinstance(issues_list, list):
            return issues_list
        return []
