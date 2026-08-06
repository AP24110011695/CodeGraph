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
        # Try multiple markers for compatibility
        markers = ["TOOL ANALYSIS:", "Tool Execution Results:"]
        tool_section = ""
        
        for marker in markers:
            if marker in prompt:
                section = prompt.split(marker, 1)[1]
                # Stop at next major section (but not REPOSITORY CONTEXT which may come before)
                for next_marker in ["Agent Collaboration Summary:", "User Question:", "Conversation History:", "ANSWER RULES:"]:
                    if next_marker in section:
                        section = section.split(next_marker, 1)[0]
                tool_section = section.strip()
                logger.debug("Found tool results using marker: %s", marker)
                break
        
        if not tool_section:
            logger.debug("Tool Execution Results section not found in prompt")
        
        return tool_section
    
    @staticmethod
    def extract_question(prompt: str) -> str:
        """Extract the user question from the prompt.
        
        Args:
            prompt: The full prompt string
            
        Returns:
            The user question string
        """
        # Try multiple markers for compatibility
        markers = ["USER QUESTION:", "User Question:"]
        for marker in markers:
            if marker in prompt:
                section = prompt.split(marker, 1)[1]
                # Get first line (the question)
                question = section.strip().split("\n", 1)[0].strip()
                logger.debug("Found question using marker: %s", marker)
                return question
        
        logger.debug("User Question section not found in prompt, defaulting to empty")
        return ""
    
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
            # Handle format: "TOOL ANALYSIS: TOOL NAME"
            if line.startswith("TOOL ANALYSIS:"):
                current_tool = line.replace("TOOL ANALYSIS:", "").strip().lower().replace(" ", "_")
                tool_data[current_tool] = {"summary": "", "data": "", "evidence": "", "related_files": ""}
            # Handle legacy format: "[TOOL NAME]"
            elif line.startswith("[") and line.endswith("]"):
                current_tool = line[1:-1]
                tool_data[current_tool] = {"summary": "", "data": "", "evidence": "", "related_files": ""}
            # Handle simple tool name on its own line (like "RAG")
            elif line and not line.startswith(("Summary:", "Evidence:", "Related Files:", "Confidence:", "TOOL ANALYSIS:", "[", "FILE:")) and not current_tool:
                current_tool = line.strip().lower()
                tool_data[current_tool] = {"summary": "", "data": "", "evidence": "", "related_files": ""}
            elif current_tool:
                if line.startswith("Summary:"):
                    tool_data[current_tool]["summary"] = line.replace("Summary:", "").strip()
                elif line.startswith("Evidence:"):
                    # Extract multiple lines of evidence
                    evidence_start = lines.index(line)
                    evidence_lines = [line.replace("Evidence:", "").strip()]
                    for next_line in lines[evidence_start + 1:]:
                        if next_line.strip() and not next_line.startswith(("Summary:", "Evidence:", "Related Files:", "Confidence:", "TOOL ANALYSIS:", "[", "FILE:")):
                            evidence_lines.append(next_line.strip())
                        else:
                            break
                    tool_data[current_tool]["evidence"] = "\n".join(evidence_lines)
                elif line.startswith("Related Files:"):
                    tool_data[current_tool]["related_files"] = line.replace("Related Files:", "").strip()
                elif line.startswith("Data:"):
                    tool_data[current_tool]["data"] = line.replace("Data:", "").strip()
        
        logger.debug("Parsed %d tool outputs from prompt", len(tool_data))
        return tool_data
