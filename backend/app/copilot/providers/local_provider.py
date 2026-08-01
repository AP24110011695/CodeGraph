"""Local heuristic provider for Copilot.

Uses deterministic synthesis and formatting instead of LLM generation.
"""

import logging
from typing import Any

from app.ai.llm_client import LLMProvider, LLMError
from ..response.synthesizer import ResponseSynthesizer
from ..response.formatter import MarkdownFormatter
from ..response.prompt_parser import PromptParser

logger = logging.getLogger(__name__)


class LocalHeuristicProvider(LLMProvider):
    """Deterministic local provider used when no cloud key is configured.
    
    This provider uses structured extractors, synthesizers, and formatters
    to generate responses without requiring an LLM API.
    """

    def __init__(self) -> None:
        self.synthesizer = ResponseSynthesizer()
        self.formatter = MarkdownFormatter()
        self.prompt_parser = PromptParser()

    def generate(self, prompt: str, **kwargs: Any) -> str:
        """Generate a response using local synthesis.
        
        Args:
            prompt: The full prompt containing tool results and user question
            **kwargs: Additional arguments (unused in local provider)
            
        Returns:
            Formatted markdown response string
            
        Raises:
            LLMError: If synthesis fails
        """
        try:
            # Extract structured information from prompt
            tool_section = self.prompt_parser.extract_tool_results(prompt)
            question = self.prompt_parser.extract_question(prompt)
            intent = self.prompt_parser.extract_intent(prompt)
            
            if tool_section and question:
                # Parse tool data
                tool_data = self.prompt_parser.parse_tool_data(tool_section)
                
                # Synthesize structured response
                response = self.synthesizer.synthesize(tool_data, intent, question)
                
                # Format as markdown
                return self.formatter.format(response, question)
            
            # Fallback to generic response
            if question:
                return (
                    f"Engineering assessment for: {question}. "
                    "Based on assembled CodeGraph intelligence (planning, memory, tools)."
                )
            return "Engineering assessment based on assembled CodeGraph intelligence."
            
        except Exception as exc:
            logger.error("LocalHeuristicProvider generation failed: %s", exc)
            raise LLMError(f"Local synthesis failed: {exc}") from exc

    def validate_config(self) -> bool:
        """Local provider always validates successfully."""
        return True
