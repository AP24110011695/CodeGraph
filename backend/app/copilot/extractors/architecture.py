"""Architecture data extractor.

Extracts structured architecture information from tool outputs.
"""

from typing import Dict, Any, List
from ..models.response_models import ArchitectureData
from .parsing_utils import ParsingUtils


class ArchitectureExtractor:
    """Extracts architecture-related data from tool outputs."""
    
    def extract(self, tool_data: Dict[str, Any]) -> ArchitectureData:
        """Extract architecture data from tool outputs.
        
        Args:
            tool_data: Dictionary mapping tool names to their output data
            
        Returns:
            ArchitectureData object with extracted information
        """
        if not tool_data:
            return ArchitectureData()
        
        data = ArchitectureData()
        
        for tool_name, tool_output in tool_data.items():
            data_str = tool_output.get("data", "") + tool_output.get("summary", "")
            
            # Extract module/node count
            module_count = ParsingUtils.extract_count(data_str, [r'(\d+)\s*module', r'(\d+)\s*node'])
            if module_count > 0:
                data.module_count = module_count
            
            # Extract dependency/relationship count
            dep_count = ParsingUtils.extract_count(data_str, [r'(\d+)\s*relationship', r'(\d+)\s*dependenc', r'(\d+)\s*edge'])
            if dep_count > 0:
                data.dependency_count = dep_count
            
            # Extract coupled modules
            coupled = self._extract_coupled_modules(tool_output)
            data.coupled_modules.extend(coupled)
            
            # Extract layers
            layers = self._extract_layers(tool_output)
            data.layers.extend(layers)
        
        # Remove duplicates
        data.coupled_modules = list(set(data.coupled_modules))
        data.layers = list(set(data.layers))
        
        # Generate placeholder module names if count exists but no names
        if data.module_count > 0 and not data.modules:
            data.modules = [f"Module_{i+1}" for i in range(min(data.module_count, 20))]
        
        # Default layers if none found
        if not data.layers and data.module_count > 0:
            data.layers = ["Presentation", "Business", "Data"]
        
        return data
    
    def _extract_coupled_modules(self, tool_output: Dict[str, Any]) -> List[str]:
        """Extract highly coupled module names from tool output."""
        modules = []
        data_str = tool_output.get("data", "") + tool_output.get("summary", "")
        
        if "highly_coupled" in data_str or "coupled" in data_str.lower():
            module_list = ParsingUtils.extract_list(data_str)
            if module_list:
                modules.extend(module_list)
        
        return modules
    
    def _extract_layers(self, tool_output: Dict[str, Any]) -> List[str]:
        """Extract layer names from tool output."""
        layers = []
        data_str = tool_output.get("data", "") + tool_output.get("summary", "")
        
        if "layer" in data_str.lower():
            layer_keywords = ["presentation", "ui", "frontend", "business", "service", 
                            "logic", "data", "persistence", "backend", "api"]
            for keyword in layer_keywords:
                if keyword in data_str.lower():
                    if keyword.capitalize() not in layers:
                        layers.append(keyword.capitalize())
        
        return layers
