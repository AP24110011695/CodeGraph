"""Sequence builder for API dependency flow engine.

Builds sequence diagrams in Mermaid format.
"""

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class SequenceResult:
    """Result from sequence building."""

    mermaid: str
    statistics: dict[str, int]


class SequenceBuilder:
    """Builds sequence diagrams from flows.

    Reuses outputs from:
    - Flow Builder
    - Endpoint Detector
    """

    def __init__(self):
        """Initialize the sequence builder."""
        pass

    def build_sequence(
        self,
        endpoints: list[Any],
        flows: list[Any],
    ) -> SequenceResult:
        """Build sequence diagram in Mermaid format.

        Args:
            endpoints: List of endpoints.
            flows: List of flow steps.

        Returns:
            SequenceResult with Mermaid diagram and statistics.
        """
        # Build Mermaid sequence diagram
        mermaid = self._build_mermaid_sequence(endpoints, flows)

        # Calculate statistics
        statistics = self._calculate_statistics(endpoints, flows)

        return SequenceResult(
            mermaid=mermaid,
            statistics=statistics,
        )

    def _build_mermaid_sequence(
        self,
        endpoints: list[Any],
        flows: list[Any],
    ) -> str:
        """Build Mermaid sequence diagram.

        Args:
            endpoints: List of endpoints.
            flows: List of flow steps.

        Returns:
            Mermaid sequence diagram string.
        """
        lines = ["sequenceDiagram"]

        # Collect all participants
        participants = set()
        for endpoint in endpoints:
            participants.add(endpoint.controller)
        for flow in flows:
            participants.add(flow.source)
            participants.add(flow.destination)

        # Add participants
        for participant in sorted(participants):
            lines.append(f'  participant {participant}')

        # Add flows
        for flow in flows[:20]:  # Limit to 20 flows
            lines.append(f'  {flow.source} ->> {flow.destination}: {flow.action}')

        return "\n".join(lines)

    def _calculate_statistics(
        self,
        endpoints: list[Any],
        flows: list[Any],
    ) -> dict[str, int]:
        """Calculate flow statistics.

        Args:
            endpoints: List of endpoints.
            flows: List of flow steps.

        Returns:
            Statistics dictionary.
        """
        controllers = set(e.controller for e in endpoints)
        middlewares = set()
        for e in endpoints:
            middlewares.update(e.middleware)

        return {
            "endpoints": len(endpoints),
            "controllers": len(controllers),
            "middlewares": len(middlewares),
            "service_calls": len(flows),
        }


sequence_builder = SequenceBuilder()
