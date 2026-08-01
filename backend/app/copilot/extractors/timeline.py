"""Timeline data extractor.

Extracts structured timeline information from tool outputs.
"""

import re
from typing import Dict, Any, List
from ..models.response_models import TimelineData
from .parsing_utils import ParsingUtils


class TimelineExtractor:
    """Extracts timeline-related data from tool outputs."""
    
    def extract(self, tool_data: Dict[str, Any]) -> TimelineData:
        """Extract timeline data from tool outputs.
        
        Args:
            tool_data: Dictionary mapping tool names to their output data
            
        Returns:
            TimelineData object with extracted information
        """
        if not tool_data:
            return TimelineData()
        
        data = TimelineData()
        
        for tool_name, tool_output in tool_data.items():
            data_str = tool_output.get("data", "")
            summary_str = tool_output.get("summary", "")
            
            # Extract commit count
            commit_count = ParsingUtils.extract_count(summary_str, [r'(\d+)\s*commit'])
            if commit_count > 0:
                data.commit_count = commit_count
            
            # Extract recent commits
            commits = self._extract_recent_commits(tool_output)
            data.recent_commits.extend(commits)
            
            # Extract files changed
            files = self._extract_files_changed(tool_output)
            data.files_changed.extend(files)
            
            # Extract affected subsystems
            subsystems = self._extract_affected_subsystems(tool_output)
            data.affected_subsystems.extend(subsystems)
        
        # Remove duplicates
        data.files_changed = list(set(data.files_changed))
        data.affected_subsystems = list(set(data.affected_subsystems))
        
        return data
    
    def _extract_recent_commits(self, tool_output: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract recent commits from tool output."""
        data_str = tool_output.get("data", "")
        
        if "commit" not in data_str.lower():
            return []
        
        commits_list = ParsingUtils.extract_list(data_str)
        if isinstance(commits_list, list):
            return commits_list[:10]
        return []
    
    def _extract_files_changed(self, tool_output: Dict[str, Any]) -> List[str]:
        """Extract changed files from tool output."""
        data_str = tool_output.get("data", "") + tool_output.get("summary", "")
        return ParsingUtils.extract_file_paths(data_str)[:20]
    
    def _extract_affected_subsystems(self, tool_output: Dict[str, Any]) -> List[str]:
        """Extract affected subsystems from tool output."""
        subsystems = []
        data_str = tool_output.get("data", "") + tool_output.get("summary", "")
        
        if "subsystem" in data_str.lower() or "component" in data_str.lower():
            # Look for subsystem names in various formats
            matches = re.findall(r'(subsystem|component)\s*[:\s]+([\w-]+)', data_str, re.IGNORECASE)
            for _, name in matches:
                if name not in subsystems:
                    subsystems.append(name.capitalize())
            
            # Also look for capitalized words that might be subsystem names
            if not matches:
                words = ParsingUtils.extract_capitalized_words(data_str, exclude=['subsystem', 'component', 'data', 'summary', 'recent'])
                subsystems.extend(words)
        
        return subsystems[:5]
