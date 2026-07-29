"""Localization ranker for bug localization engine.

Ranks potential bug locations based on collected evidence.
"""

import logging
from collections import defaultdict
from dataclasses import dataclass, field

from app.bug_localization.evidence_collector import BugEvidence

logger = logging.getLogger(__name__)


@dataclass
class BugPrediction:
    """A bug location prediction."""

    file: str
    function: str | None = None
    module: str | None = None
    confidence: int = 50
    priority: int = 1
    reason: str = ""
    evidence: str = ""


class LocalizationRanker:
    """Ranks potential bug locations based on collected evidence.

    Uses evidence from multiple sources to calculate confidence scores.
    """

    def __init__(self):
        """Initialize the localization ranker."""
        pass

    def rank_predictions(
        self,
        evidence: list[BugEvidence],
        bug_description: str,
    ) -> list[BugPrediction]:
        """Rank potential bug locations based on evidence.

        Args:
            evidence: List of collected evidence.
            bug_description: Description of the bug.

        Returns:
            List of ranked bug predictions.
        """
        if not evidence:
            return []

        # Group evidence by file
        file_evidence: dict[str, list[BugEvidence]] = defaultdict(list)
        for ev in evidence:
            file_evidence[ev.file].append(ev)

        # Calculate scores for each file
        predictions: list[BugPrediction] = []
        for file_path, file_evs in file_evidence.items():
            prediction = self._calculate_prediction(file_path, file_evs, bug_description)
            predictions.append(prediction)

        # Sort by confidence (descending)
        predictions.sort(key=lambda p: p.confidence, reverse=True)

        # Assign priorities
        for i, prediction in enumerate(predictions):
            prediction.priority = i + 1

        return predictions

    def _calculate_prediction(
        self,
        file_path: str,
        evidence: list[BugEvidence],
        bug_description: str,
    ) -> BugPrediction:
        """Calculate prediction for a file based on evidence.

        Args:
            file_path: The file path.
            evidence: List of evidence for this file.
            bug_description: Description of the bug.

        Returns:
            BugPrediction with calculated confidence and evidence.
        """
        # Calculate weighted confidence
        total_confidence = 0
        total_relevance = 0
        evidence_sources = set()
        evidence_summary = []

        for ev in evidence:
            # Weight confidence by relevance
            weighted_confidence = ev.confidence * (ev.relevance_score / 100)
            total_confidence += weighted_confidence
            total_relevance += ev.relevance_score
            evidence_sources.add(ev.source)
            evidence_summary.append(f"{ev.source}: {ev.evidence}")

        # Normalize confidence
        if evidence:
            avg_confidence = total_confidence / len(evidence)
            avg_relevance = total_relevance / len(evidence)
        else:
            avg_confidence = 50
            avg_relevance = 50

        # Boost confidence if multiple sources agree
        source_boost = min(20, len(evidence_sources) * 5)

        # Calculate final confidence
        final_confidence = min(100, int(avg_confidence + source_boost))

        # Extract function and module from evidence
        function = None
        module = None
        for ev in evidence:
            if ev.function and not function:
                function = ev.function
            if ev.module and not module:
                module = ev.module

        # Generate reason
        reason = self._generate_reason(evidence_sources, avg_relevance, bug_description)

        # Combine evidence
        combined_evidence = "; ".join(evidence_summary[:3])  # Limit to top 3 evidence items

        return BugPrediction(
            file=file_path,
            function=function,
            module=module,
            confidence=final_confidence,
            priority=1,
            reason=reason,
            evidence=combined_evidence,
        )

    def _generate_reason(self, sources: set[str], relevance: int, bug_description: str) -> str:
        """Generate a reason for the prediction.

        Args:
            sources: Set of evidence sources.
            relevance: Average relevance score.
            bug_description: Description of the bug.

        Returns:
            Reason string.
        """
        if not sources:
            return "Limited evidence available."

        source_list = sorted(sources)
        if len(source_list) == 1:
            source_text = source_list[0]
        elif len(source_list) == 2:
            source_text = f"{source_list[0]} and {source_list[1]}"
        else:
            source_text = f"{', '.join(source_list[:-1])}, and {source_list[-1]}"

        if relevance > 70:
            relevance_text = "highly relevant"
        elif relevance > 50:
            relevance_text = "relevant"
        else:
            relevance_text = "potentially relevant"

        return f"Evidence from {source_text} indicates this file is {relevance_text} to the bug description."


localization_ranker = LocalizationRanker()
