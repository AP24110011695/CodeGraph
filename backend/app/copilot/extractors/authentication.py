"""Authentication data extractor.

Extracts structured authentication information from tool outputs.
"""

from typing import Dict, Any, List
from ..models.response_models import AuthenticationData


class AuthenticationExtractor:
    """Extracts authentication-related data from tool outputs."""
    
    def extract(self, tool_data: Dict[str, Any]) -> AuthenticationData:
        """Extract authentication data from tool outputs.
        
        Args:
            tool_data: Dictionary mapping tool names to their output data
            
        Returns:
            AuthenticationData object with extracted information
        """
        if not tool_data:
            return AuthenticationData()
        
        data = AuthenticationData()
        
        for tool_name, tool_output in tool_data.items():
            data_str = tool_output.get("data", "") + tool_output.get("summary", "")
            
            # Extract components
            components = self._extract_components(tool_output)
            data.components.extend(components)
        
        # Remove duplicates
        data.components = list(set(data.components))
        
        # Default components if none found
        if not data.components:
            data.components = ["Authentication Service", "User Management", "Session Handler"]
        
        # Generate flow description
        data.flow_description = self._generate_flow_description(data.components)
        
        return data
    
    def _extract_components(self, tool_output: Dict[str, Any]) -> List[str]:
        """Extract authentication components from tool output."""
        components = []
        auth_keywords = ["auth", "login", "user", "session", "token", "oauth", "jwt", "password"]
        data_str = tool_output.get("data", "") + tool_output.get("summary", "")
        
        for keyword in auth_keywords:
            if keyword in data_str.lower():
                if keyword.capitalize() not in components:
                    components.append(keyword.capitalize())
        
        return components
    
    def _generate_flow_description(self, components: List[str]) -> str:
        """Generate authentication flow description."""
        return "The authentication flow typically involves: 1) User submits credentials, 2) System validates credentials, 3) Session/token is generated, 4) User is granted access to protected resources."
