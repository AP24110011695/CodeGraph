"""Metrics data extractor.

Extracts structured metrics information from tool outputs.
"""

import re
from typing import Dict, Any, List, Tuple
from ..models.response_models import MetricsData
from .parsing_utils import ParsingUtils


class MetricsExtractor:
    """Extracts metrics-related data from tool outputs."""
    
    def extract(self, tool_data: Dict[str, Any]) -> MetricsData:
        """Extract metrics data from tool outputs.
        
        Args:
            tool_data: Dictionary mapping tool names to their output data
            
        Returns:
            MetricsData object with extracted information
        """
        if not tool_data:
            return MetricsData()
        
        data = MetricsData()
        all_languages = {}
        
        for tool_name, tool_output in tool_data.items():
            data_str = tool_output.get("data", "") + tool_output.get("summary", "")
            
            # Extract file count
            file_count = ParsingUtils.extract_count(data_str, [r'(\d+)\s*file'])
            if file_count > 0:
                data.file_count = file_count
            
            # Extract repository size
            size_match = re.search(r'(\d+(?:\.\d+)?)\s*(MB|GB|KB)', data_str, re.IGNORECASE)
            if size_match:
                data.repo_size = f"{size_match.group(1)} {size_match.group(2)}"
            
            # Extract languages
            languages = self._extract_languages(tool_output)
            for lang, count in languages:
                all_languages[lang] = all_languages.get(lang, 0) + count
            
            # Extract frameworks
            frameworks = self._extract_frameworks(tool_output)
            data.frameworks.extend(frameworks)
            
            # Extract largest directories
            dirs = self._extract_largest_directories(tool_output)
            data.largest_directories.extend(dirs)
        
        # Sort languages by count
        data.languages = sorted(all_languages.items(), key=lambda x: x[1], reverse=True)
        
        # Remove duplicates and sort frameworks
        data.frameworks = list(set(data.frameworks))
        
        # Sort directories by count
        data.largest_directories = sorted(set(data.largest_directories), key=lambda x: x[1], reverse=True)
        
        return data
    
    def _extract_languages(self, tool_output: Dict[str, Any]) -> List[Tuple[str, int]]:
        """Extract language information from tool output."""
        languages = []
        data_str = tool_output.get("data", "")
        
        if "languages" in data_str:
            # Try to find the nested languages dictionary
            lang_dict = ParsingUtils.extract_dict(data_str, "languages")
            if lang_dict:
                for lang, count in lang_dict.items():
                    languages.append((lang, count))
            else:
                # Try to find the outer dict and extract languages from it
                outer_dict = ParsingUtils.extract_dict(data_str)
                if outer_dict and "languages" in outer_dict:
                    lang_dict = outer_dict["languages"]
                    for lang, count in lang_dict.items():
                        languages.append((lang, count))
        
        # Fallback to summary parsing
        if not languages:
            summary = tool_output.get("summary", "")
            if "detected:" in summary:
                parts = summary.split("detected:")[1].strip()
                matches = re.findall(r'(\w+)\s*\((\d+)\)', parts)
                for lang, count in matches:
                    languages.append((lang, int(count)))
        
        # Another fallback: try to parse the raw data string directly
        if not languages and data_str:
            matches = re.findall(r'["\']?(\w+)["\']?\s*:\s*(\d+)', data_str)
            for lang, count in matches:
                if lang.lower() not in ['node_count', 'edge_count', 'total', 'summary', 'languages']:
                    languages.append((lang, int(count)))
        
        return languages
    
    def _extract_frameworks(self, tool_output: Dict[str, Any]) -> List[str]:
        """Extract framework names from tool output."""
        frameworks = []
        framework_keywords = ["react", "vue", "angular", "django", "flask", "fastapi", 
                            "spring", "express", "next", "nuxt"]
        data_str = tool_output.get("data", "") + tool_output.get("summary", "")
        
        for fw in framework_keywords:
            if fw in data_str.lower():
                if fw.capitalize() not in frameworks:
                    frameworks.append(fw.capitalize())
        
        return frameworks
    
    def _extract_largest_directories(self, tool_output: Dict[str, Any]) -> List[Tuple[str, int]]:
        """Extract largest directories from tool output."""
        dirs = []
        data_str = tool_output.get("data", "") + tool_output.get("summary", "")
        
        # Look for directory patterns
        dir_matches = re.findall(r'([\w/_-]+)\s*:\s*(\d+)\s*file', data_str)
        for dir_name, count in dir_matches:
            dirs.append((dir_name, int(count)))
        
        return dirs
