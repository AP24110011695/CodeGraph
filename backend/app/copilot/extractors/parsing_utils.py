"""Shared parsing utilities for extractors.

Provides common parsing functions to avoid duplicate code across extractors.
"""

import ast
import re
import logging
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)


class ParsingUtils:
    """Shared parsing utilities for extracting data from tool outputs."""
    
    @staticmethod
    def extract_count(data_str: str, patterns: List[str]) -> int:
        """Extract a count from data string using multiple patterns.
        
        Args:
            data_str: String containing the data
            patterns: List of regex patterns to try
            
        Returns:
            Extracted count as integer, or 0 if not found
        """
        for pattern in patterns:
            match = re.search(pattern, data_str, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1))
                except (ValueError, IndexError):
                    continue
        return 0
    
    @staticmethod
    def extract_list(data_str: str, start_marker: str = "[") -> List[Any]:
        """Extract a list from data string using AST parsing.
        
        Args:
            data_str: String containing the list
            start_marker: Character that starts the list (default: '[')
            
        Returns:
            Parsed list, or empty list if parsing fails
        """
        if start_marker not in data_str:
            return []
        
        try:
            start = data_str.find(start_marker)
            bracket_count = 0
            for i, char in enumerate(data_str[start:], start):
                if char == start_marker:
                    bracket_count += 1
                elif char == "]" if start_marker == "[" else "}":
                    bracket_count -= 1
                    if bracket_count == 0:
                        list_str = data_str[start:i+1]
                        parsed = ast.literal_eval(list_str)
                        if isinstance(parsed, list):
                            return parsed
                        break
        except Exception as e:
            logger.debug("Failed to parse list from data: %s", e)
        
        return []
    
    @staticmethod
    def extract_dict(data_str: str, key_hint: str = None) -> Dict[str, Any]:
        """Extract a dictionary from data string using AST parsing.
        
        Args:
            data_str: String containing the dictionary
            key_hint: Optional hint to find the specific dict (e.g., "summary")
            
        Returns:
            Parsed dictionary, or empty dict if parsing fails
        """
        try:
            if key_hint:
                # Try to find dict with specific key hint
                pattern = rf"{key_hint}['\"]?\s*:\s*(\{{[^}}]*\}})"
                match = re.search(pattern, data_str)
                if match:
                    dict_str = match.group(1)
                    return ast.literal_eval(dict_str)
            
            # Fallback: find first dict
            if "{" in data_str:
                start = data_str.find("{")
                bracket_count = 0
                for i, char in enumerate(data_str[start:], start):
                    if char == "{":
                        bracket_count += 1
                    elif char == "}":
                        bracket_count -= 1
                        if bracket_count == 0:
                            dict_str = data_str[start:i+1]
                            return ast.literal_eval(dict_str)
        except Exception as e:
            logger.debug("Failed to parse dict from data: %s", e)
        
        return {}
    
    @staticmethod
    def extract_file_paths(data_str: str, extensions: List[str] = None) -> List[str]:
        """Extract file paths from data string.
        
        Args:
            data_str: String containing file paths
            extensions: List of file extensions to match (e.g., ['py', 'js'])
            
        Returns:
            List of unique file paths
        """
        if extensions is None:
            extensions = ['py', 'js', 'ts', 'java', 'go', 'rs', 'cpp', 'h', 'tsx', 'jsx', 'vue', 'rb', 'php', 'cs']
        
        ext_pattern = '|'.join(extensions)
        pattern = rf'[\w/_.-]+\.({ext_pattern})'
        matches = re.findall(pattern, data_str)
        return list(set(matches))
    
    @staticmethod
    def extract_capitalized_words(data_str: str, min_length: int = 3, exclude: List[str] = None) -> List[str]:
        """Extract capitalized words from data string.
        
        Args:
            data_str: String containing words
            min_length: Minimum word length to include
            exclude: Words to exclude from results
            
        Returns:
            List of unique capitalized words
        """
        if exclude is None:
            exclude = ['subsystem', 'component', 'data', 'summary', 'recent']
        
        words = re.findall(r'\b[A-Z][a-z]+\b', data_str)
        filtered = [w for w in words if len(w) >= min_length and w.lower() not in exclude]
        return list(set(filtered))
