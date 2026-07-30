"""Pydantic schemas for Intelligent Code Impact Analysis (CG-068)."""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ChangeTarget(BaseModel):
    """Normalized change target. Designed for future Git diff / PR analysis."""

    target: str = Field(description="Class, module, file, or API symbol to analyze")
    target_type: str = Field(
        default="auto",
        description="auto | class | module | file | api | symbol",
    )
    change_type: str = Field(
        default="modify",
        description="modify | delete | rename | add — future Git/PR operations",
    )
    related_files: List[str] = Field(
        default_factory=list,
        description="Optional related paths (future: files from a diff/PR)",
    )


class ImpactAnalyzeRequest(BaseModel):
    """Request body for POST /impact/analyze/{repository_id}."""

    target: str = Field(description="What is being changed (class, API, module, file)")
    target_type: str = Field(default="auto")
    change_type: str = Field(default="modify")
    related_files: List[str] = Field(default_factory=list)
    max_depth: int = Field(default=4, ge=1, le=10, description="Propagation depth")
    query: Optional[str] = Field(
        default=None,
        description="Optional natural-language question for narrative answers",
    )


class AffectedNode(BaseModel):
    """A node predicted to be affected by the change."""

    id: str
    name: str
    node_type: str = Field(
        default="module",
        description="module | file | class | api | service | symbol",
    )
    distance: int = Field(default=0, description="Hops from the change target")
    impact_weight: float = Field(default=0.0, description="0.0–1.0 relative impact")
    reason: str = ""


class MemoryImpactResult(BaseModel):
    """Repository Memory entries predicted to need refresh after the change."""

    affected_module_memories: List[str] = Field(default_factory=list)
    affected_file_memories: List[str] = Field(default_factory=list)
    affected_symbol_memories: List[str] = Field(default_factory=list)
    affected_api_memories: List[str] = Field(default_factory=list)
    memory_refresh_recommended: bool = False
    summary: str = ""


class PropagationHop(BaseModel):
    """Single hop in a change propagation path."""

    from_id: str
    to_id: str
    edge_type: str = "depends_on"
    depth: int = 1


class PropagationPath(BaseModel):
    """Ordered propagation path from the change origin."""

    path: List[str] = Field(default_factory=list)
    hops: List[PropagationHop] = Field(default_factory=list)
    length: int = 0
    severity: str = Field(default="medium", description="low | medium | high | critical")


class DependencyImpactResult(BaseModel):
    """Dependency-level impact analysis."""

    direct_dependents: List[AffectedNode] = Field(default_factory=list)
    transitive_dependents: List[AffectedNode] = Field(default_factory=list)
    dependent_services: List[str] = Field(default_factory=list)
    dependency_blast_radius: int = 0
    summary: str = ""


class ArchitectureImpactResult(BaseModel):
    """Architecture-level impact analysis."""

    affected_modules: List[str] = Field(default_factory=list)
    affected_layers: List[str] = Field(default_factory=list)
    boundary_crossings: List[str] = Field(default_factory=list)
    coupling_pressure: float = Field(default=0.0, description="0.0–1.0")
    summary: str = ""


class APIImpactResult(BaseModel):
    """API / contract-level impact analysis."""

    affected_apis: List[str] = Field(default_factory=list)
    dependent_consumers: List[str] = Field(default_factory=list)
    breaking_change_likely: bool = False
    contract_risk: str = Field(default="low", description="low | medium | high")
    summary: str = ""


class ChangeRiskResult(BaseModel):
    """Estimated risk of applying the change."""

    risk_score: float = Field(default=0.0, description="0–100")
    risk_level: str = Field(default="low", description="low | medium | high | critical")
    factors: List[str] = Field(default_factory=list)
    hotspot_overlap: List[str] = Field(default_factory=list)
    recommendation: str = ""


class ImpactStatisticsModel(BaseModel):
    """Aggregate impact statistics."""

    nodes_analyzed: int = 0
    affected_nodes: int = 0
    propagation_paths: int = 0
    max_propagation_depth: int = 0
    dependency_impact_count: int = 0
    architecture_modules_affected: int = 0
    api_contracts_affected: int = 0
    confidence_score: float = Field(default=0.0, description="0.0–1.0")


class ImpactAnalyzeResponse(BaseModel):
    """Full intelligent impact analysis payload."""

    repository_id: str
    target: ChangeTarget
    dependency_impact: DependencyImpactResult
    architecture_impact: ArchitectureImpactResult
    api_impact: APIImpactResult
    memory_impact: MemoryImpactResult = Field(default_factory=MemoryImpactResult)
    propagation_paths: List[PropagationPath] = Field(default_factory=list)
    risk: ChangeRiskResult
    statistics: ImpactStatisticsModel
    what_breaks: List[str] = Field(default_factory=list)
    affected_modules: List[str] = Field(default_factory=list)
    affected_services: List[str] = Field(default_factory=list)
    affected_apis: List[str] = Field(default_factory=list)
    affected_symbols: List[str] = Field(default_factory=list)
    affected_repository_memory: List[str] = Field(
        default_factory=list,
        description="Memory keys/paths predicted to require refresh",
    )
    impact_summary: str = Field(default="", description="Generated executive impact summary")
    narrative: str = ""
    confidence_score: float = 0.0
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class ImpactSummaryResponse(BaseModel):
    """Lightweight repository-level impact summary."""

    repository_id: str
    high_risk_targets: List[str] = Field(default_factory=list)
    critical_modules: List[str] = Field(default_factory=list)
    critical_apis: List[str] = Field(default_factory=list)
    critical_services: List[str] = Field(default_factory=list)
    average_blast_radius: float = 0.0
    confidence_score: float = 0.0
    summary: str = ""
    last_analyzed_targets: List[str] = Field(default_factory=list)
