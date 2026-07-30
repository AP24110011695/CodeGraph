"""Intelligent Code Impact Analysis module (CG-068)."""

from .api_impact import APIImpact
from .architecture_impact import ArchitectureImpact
from .change_propagation import ChangePropagation
from .dependency_impact import DependencyImpact
from .impact_engine import ImpactEngine, impact_engine
from .impact_statistics import ImpactStatistics
from .memory_impact import MemoryImpact
from .risk_analyzer import RiskAnalyzer

__all__ = [
    "APIImpact",
    "ArchitectureImpact",
    "ChangePropagation",
    "DependencyImpact",
    "ImpactEngine",
    "ImpactStatistics",
    "MemoryImpact",
    "RiskAnalyzer",
    "impact_engine",
]
