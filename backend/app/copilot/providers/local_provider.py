"""Local heuristic provider for Copilot.

Uses deterministic synthesis and formatting instead of LLM generation.
"""

import logging
from typing import Any

from app.ai.llm_client import LLMProvider, LLMError
from ..response.synthesizer import ResponseSynthesizer
from ..response.formatter import MarkdownFormatter
from ..response.prompt_parser import PromptParser
from ..response.report_synthesizer import ReportSynthesizer
from ..response.executive_formatter import ExecutiveReportFormatter

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
        self.report_synthesizer = ReportSynthesizer()
        self.executive_formatter = ExecutiveReportFormatter()

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
                
                # Check if this is an executive report request
                if self._is_executive_report_request(question, intent):
                    # Use executive report pipeline
                    response = self.synthesizer.synthesize(tool_data, intent, question)
                    report_data = self.report_synthesizer.synthesize_executive_report(response, question, tool_data)
                    return self.executive_formatter.format(report_data, question)
                else:
                    # Use standard pipeline for single-domain queries
                    response = self.synthesizer.synthesize(tool_data, intent, question)
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

    def _is_executive_report_request(self, question: str, intent: str) -> bool:
        """Determine if the request is for an executive report.
        
        Args:
            question: The user's question
            intent: The detected intent
            
        Returns:
            True if this is an executive report request
        """
        question_lower = question.lower()
        intent_lower = intent.lower()
        
        # Keywords that indicate executive report request
        executive_keywords = [
            'executive report',
            'comprehensive report',
            'full report',
            'complete report',
            'overall report',
            'generate report',
            'health report',
            'assessment report',
            'engineering report',
            'detailed report'
        ]
        
        # Check if question contains executive keywords
        for keyword in executive_keywords:
            if keyword in question_lower:
                return True
        
        # Check if intent is health/report (which typically requires comprehensive output)
        if 'health' in intent_lower or 'report' in intent_lower:
            return True
        
        return False

    def validate_config(self) -> bool:
        """Local provider always validates successfully."""
        return True
