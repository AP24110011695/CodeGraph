"""Change risk estimation for impact analysis.

Composes blast-radius signals with Timeline hotspots. Does not reimplement
the repository Risk Engine scoring pipeline.
"""

from __future__ import annotations

from typing import List, Optional

from app.schemas.impact_analysis import (
    APIImpactResult,
    ArchitectureImpactResult,
    ChangeRiskResult,
    DependencyImpactResult,
    PropagationPath,
)


class RiskAnalyzer:
    """Estimates the risk of applying a proposed change."""

    def analyze(
        self,
        dependency_impact: DependencyImpactResult,
        architecture_impact: ArchitectureImpactResult,
        api_impact: APIImpactResult,
        propagation_paths: List[PropagationPath],
        hotspot_paths: Optional[List[str]] = None,
        change_type: str = "modify",
    ) -> ChangeRiskResult:
        factors: List[str] = []
        score = 0.0

        blast = dependency_impact.dependency_blast_radius
        score += min(40.0, blast * 4.0)
        if blast >= 8:
            factors.append(f"Large dependency blast radius ({blast})")
        elif blast >= 3:
            factors.append(f"Moderate dependency blast radius ({blast})")

        score += architecture_impact.coupling_pressure * 25.0
        if architecture_impact.coupling_pressure >= 0.5:
            factors.append(f"Elevated architectural coupling ({architecture_impact.coupling_pressure})")

        if architecture_impact.boundary_crossings:
            score += min(15.0, len(architecture_impact.boundary_crossings) * 3)
            factors.append(
                f"{len(architecture_impact.boundary_crossings)} architecture boundary crossing(s)"
            )

        if api_impact.breaking_change_likely:
            score += 20.0
            factors.append("Breaking API change likely")
        elif api_impact.contract_risk == "high":
            score += 12.0
            factors.append("High API contract risk")
        elif api_impact.affected_apis:
            score += 6.0
            factors.append(f"{len(api_impact.affected_apis)} API(s) in impact set")

        critical_paths = [p for p in propagation_paths if p.severity in ("high", "critical")]
        if critical_paths:
            score += min(15.0, len(critical_paths) * 3)
            factors.append(f"{len(critical_paths)} high-severity propagation path(s)")

        hotspot_overlap: List[str] = []
        if hotspot_paths:
            impacted_names = {
                n.name.lower()
                for n in dependency_impact.direct_dependents + dependency_impact.transitive_dependents
            }
            impacted_names.update(m.lower() for m in architecture_impact.affected_modules)
            for hot in hotspot_paths:
                if any(part and part in hot.lower() for part in impacted_names) or any(
                    hot.lower() in name for name in impacted_names
                ):
                    hotspot_overlap.append(hot)
            if hotspot_overlap:
                score += min(15.0, len(hotspot_overlap) * 5)
                factors.append(f"Overlaps {len(hotspot_overlap)} timeline hotspot(s)")

        if change_type in ("delete", "rename"):
            score += 10.0
            factors.append(f"Destructive change_type={change_type}")

        score = round(min(100.0, score), 1)
        level = self._level(score)
        recommendation = self._recommendation(level, factors)

        if not factors:
            factors.append("Limited blast radius with low coupling pressure")

        return ChangeRiskResult(
            risk_score=score,
            risk_level=level,
            factors=factors,
            hotspot_overlap=hotspot_overlap[:10],
            recommendation=recommendation,
        )

    def _level(self, score: float) -> str:
        if score >= 75:
            return "critical"
        if score >= 50:
            return "high"
        if score >= 25:
            return "medium"
        return "low"

    def _recommendation(self, level: str, factors: List[str]) -> str:
        if level in ("critical", "high"):
            return (
                "Stage the change behind feature flags, add contract tests for affected APIs, "
                "and review propagation paths with owning teams before merge."
            )
        if level == "medium":
            return (
                "Add focused regression coverage for direct dependents and verify "
                "boundary crossings before release."
            )
        return "Low predicted impact — proceed with standard review and targeted unit tests."
