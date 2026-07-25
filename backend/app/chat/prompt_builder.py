"""Prompt builder for AI-powered repository chat."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class PromptBuilder:
    """Builds structured prompts for LLM-based repository chat."""

    def __init__(self, max_context_length: int = 8000) -> None:
        """Initialize the prompt builder.

        Args:
            max_context_length: Maximum length of context in characters
        """
        self.max_context_length = max_context_length

    def build_prompt(
        self,
        user_question: str,
        retrieved_chunks: list[dict[str, Any]],
        architecture_summary: dict[str, Any],
        framework_summary: list[str],
        dependency_summary: dict[str, Any],
        conversation_history: list[dict[str, str]] | None = None,
    ) -> str:
        """Build a structured prompt for the LLM.

        Args:
            user_question: The user's question
            retrieved_chunks: List of retrieved code chunks
            architecture_summary: Architecture analysis summary
            framework_summary: List of detected frameworks
            dependency_summary: Dependency graph summary
            conversation_history: Optional conversation history

        Returns:
            The structured prompt
        """
        sections = []

        # System instruction
        sections.append(self._build_system_instruction())

        # Repository context
        sections.append(self._build_repository_context(
            architecture_summary,
            framework_summary,
            dependency_summary
        ))

        # Retrieved code chunks
        sections.append(self._build_retrieved_chunks(retrieved_chunks))

        # Conversation history
        if conversation_history:
            sections.append(self._build_conversation_history(conversation_history))

        # User question
        sections.append(f"\nUser Question:\n{user_question}")

        # Combine and truncate if necessary
        prompt = "\n".join(sections)
        if len(prompt) > self.max_context_length:
            prompt = self._truncate_prompt(prompt, self.max_context_length)

        return prompt

    def _build_system_instruction(self) -> str:
        """Build the system instruction section."""
        return """You are an AI software architect assistant helping a developer understand a codebase.

Your task is to answer questions about the repository based ONLY on the provided context.

Rules:
- Answer using ONLY the information from the retrieved code chunks, architecture summary, framework detection, and dependency summary.
- If there is insufficient evidence in the provided context, respond with: "I could not find enough evidence in this repository."
- Never hallucinate APIs, functions, or architecture components not present in the context.
- Be specific and reference the actual code when possible.
- Keep answers concise and focused on the question."""

    def _build_repository_context(
        self,
        architecture_summary: dict[str, Any],
        framework_summary: list[str],
        dependency_summary: dict[str, Any],
    ) -> str:
        """Build the repository context section.

        Args:
            architecture_summary: Architecture analysis results
            framework_summary: List of detected frameworks
            dependency_summary: Dependency graph summary

        Returns:
            The repository context string
        """
        sections = ["\nRepository Context:"]

        # Architecture
        if architecture_summary:
            sections.append("\nArchitecture:")
            project_name = architecture_summary.get("project", {}).get("name", "Unknown")
            sections.append(f"  Project: {project_name}")

            modules = architecture_summary.get("modules", [])
            if modules:
                sections.append(f"  Modules ({len(modules)}):")
                for module in modules[:10]:  # Limit to 10 modules
                    sections.append(f"    - {module.get('name', 'Unknown')} ({module.get('type', 'Unknown')})")

            layers = architecture_summary.get("layers", [])
            if layers:
                sections.append(f"  Layers: {', '.join(layers)}")

        # Frameworks
        if framework_summary:
            sections.append(f"\nDetected Frameworks: {', '.join(framework_summary)}")

        # Dependencies
        if dependency_summary:
            sections.append("\nDependencies:")
            stats = dependency_summary.get("statistics", {})
            if stats:
                sections.append(f"  Total files: {stats.get('files', 0)}")
                sections.append(f"  Total dependencies: {stats.get('dependencies', 0)}")

        return "\n".join(sections)

    def _build_retrieved_chunks(self, chunks: list[dict[str, Any]]) -> str:
        """Build the retrieved chunks section.

        Args:
            chunks: List of retrieved code chunks

        Returns:
            The retrieved chunks string
        """
        if not chunks:
            return "\nRetrieved Code Chunks: None"

        sections = ["\nRetrieved Code Chunks:"]
        for i, chunk in enumerate(chunks[:10], 1):  # Limit to 10 chunks
            file_path = chunk.get("file", "Unknown")
            language = chunk.get("language", "Unknown")
            content = chunk.get("content", "")
            start_line = chunk.get("start_line", 0)
            end_line = chunk.get("end_line", 0)
            score = chunk.get("score", 0.0)

            sections.append(f"\n{i}. {file_path} ({language}) [Lines {start_line}-{end_line}] [Score: {score:.2f}]")
            sections.append(f"   {content[:500]}")  # Limit chunk content to 500 chars

        return "\n".join(sections)

    def _build_conversation_history(self, history: list[dict[str, str]]) -> str:
        """Build the conversation history section.

        Args:
            history: List of conversation messages

        Returns:
            The conversation history string
        """
        if not history:
            return ""

        sections = ["\nConversation History:"]
        # Get last 5 messages
        recent_history = history[-5:] if len(history) > 5 else history

        for msg in recent_history:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")[:200]  # Limit to 200 chars
            sections.append(f"  {role.capitalize()}: {content}")

        return "\n".join(sections)

    def _truncate_prompt(self, prompt: str, max_length: int) -> str:
        """Truncate prompt to fit within max length.

        Args:
            prompt: The full prompt
            max_length: Maximum length

        Returns:
            The truncated prompt
        """
        # Try to preserve the most important parts
        # Keep system instruction and user question, truncate middle
        lines = prompt.split("\n")
        system_end = 0
        question_start = len(lines)

        # Find system instruction end
        for i, line in enumerate(lines):
            if "User Question:" in line:
                question_start = i
                break
            if line.strip() and system_end == 0 and i > 5:
                system_end = i

        # Keep system instruction and question, truncate middle
        if system_end > 0 and question_start < len(lines):
            kept = lines[:system_end] + ["\n... [Context truncated to fit length limit] ...\n"] + lines[question_start:]
            return "\n".join(kept)

        # Fallback: simple truncation
        return prompt[:max_length] + "... [truncated]"
