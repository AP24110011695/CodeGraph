"""Prompt parsing utilities.

Extracts structured information from Copilot prompts.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class PromptParser:
    """Parses Copilot prompts to extract structured information."""
    
    @staticmethod
    def extract_tool_results(prompt: str) -> str:
        """Extract the Tool Execution Results section from the prompt.
        
        Args:
            prompt: The full prompt string
            
        Returns:
            String containing tool execution results
        """
        marker = "Tool Execution Results:"
        if marker not in prompt:
            logger.debug("Tool Execution Results section not found in prompt")
            return ""
        section = prompt.split(marker, 1)[1]
        # Stop at next major section
        for next_marker in ["Agent Collaboration Summary:", "User Question:", "Conversation History:"]:
            if next_marker in section:
                section = section.split(next_marker, 1)[0]
        return section.strip()
    
    @staticmethod
    def extract_question(prompt: str) -> str:
        """Extract the user question from the prompt.
        
        Args:
            prompt: The full prompt string
            
        Returns:
            The user question string
        """
        marker = "User Question:"
        if marker not in prompt:
            logger.debug("User Question section not found in prompt")
            return ""
        section = prompt.split(marker, 1)[1]
        # Get first line (the question)
        question = section.strip().split("\n", 1)[0].strip()
        return question
    
    @staticmethod
    def extract_intent(prompt: str) -> str:
        """Extract the intent from the prompt.
        
        The intent should already be determined by the IntentRouter in the pipeline.
        This method extracts it from the prompt context.
        
        Args:
            prompt: The full prompt string
            
        Returns:
            The intent string
        """
        marker = "Planning Intent:"
        if marker in prompt:
            section = prompt.split(marker, 1)[1]
            # Get the intent value (first line after marker)
            intent = section.strip().split("\n", 1)[0].strip()
            return intent
        logger.debug("Planning Intent section not found in prompt, defaulting to generic")
        return "generic"
    
    @staticmethod
    def parse_tool_data(tool_section: str) -> Dict[str, Dict[str, str]]:
        """Parse tool execution results into structured data.
        
        Args:
            tool_section: String containing tool outputs
            
        Returns:
            Dictionary mapping tool names to their summary and data
        """
        lines = tool_section.split("\n")
        tool_data: Dict[str, Dict[str, str]] = {}
        current_tool = None
        
        for line in lines:
            line = line.strip()
            if line.startswith("[") and line.endswith("]"):
                current_tool = line[1:-1]
                tool_data[current_tool] = {"summary": "", "data": ""}
            elif current_tool:
                if line.startswith("Summary:"):
                    tool_data[current_tool]["summary"] = line.replace("Summary:", "").strip()
                elif line.startswith("Data:"):
                    tool_data[current_tool]["data"] = line.replace("Data:", "").strip()
        
        logger.debug("Parsed %d tool outputs from prompt", len(tool_data))
        return tool_data
