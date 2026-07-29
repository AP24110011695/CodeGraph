"""Flow builder for API dependency flow engine.

Builds API dependency flows from endpoints and dependencies.
"""

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class FlowStep:
    """A step in the API flow."""

    source: str
    destination: str
    action: str
    evidence: str


class FlowBuilder:
    """Builds API dependency flows from endpoints.

    Reuses outputs from:
    - Endpoint Detector
    - Dependency Graph
    - Parser Engine
    """

    def __init__(self):
        """Initialize the flow builder."""
        pass

    def build_flows(
        self,
        endpoints: list[Any],
        dependency_graph: dict | None = None,
    ) -> list[FlowStep]:
        """Build API dependency flows.

        Args:
            endpoints: List of detected endpoints.
            dependency_graph: The dependency graph.

        Returns:
            List of flow steps.
        """
        flows: list[FlowStep] = []

        # Build flows from endpoint dependencies
        for endpoint in endpoints:
            for dep in endpoint.dependencies:
                flows.append(
                    FlowStep(
                        source=endpoint.controller,
                        destination=dep,
                        action=f"Call {dep}",
                        evidence=f"Dependency in {endpoint.controller}",
                    )
                )

        # Build flows from database access
        for endpoint in endpoints:
            for db in endpoint.database_access:
                flows.append(
                    FlowStep(
                        source=endpoint.controller,
                        destination=db,
                        action="Query Database",
                        evidence=f"Database access in {endpoint.controller}",
                    )
                )

        return flows


flow_builder = FlowBuilder()
