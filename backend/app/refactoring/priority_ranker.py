from app.schemas.refactoring import RefactoringSuggestion

class PriorityRanker:
    """Assigns priority to refactoring suggestions based on severity, impact, and effort."""
    
    def rank(self, suggestions: list[RefactoringSuggestion]) -> list[RefactoringSuggestion]:
        """Rank suggestions and assign priorities."""
        for suggestion in suggestions:
            suggestion.priority = self._calculate_priority(suggestion)
            
        # Sort by priority (P1 -> P4)
        suggestions.sort(key=lambda s: s.priority)
        return suggestions
        
    def _calculate_priority(self, suggestion: RefactoringSuggestion) -> str:
        # P1: Critical severity or (High severity + High impact)
        # P2: High severity or (Medium severity + High impact)
        # P3: Medium severity
        # P4: Low severity
        
        severity_score = {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(suggestion.severity.lower(), 1)
        impact_score = {"high": 3, "medium": 2, "low": 1}.get(suggestion.estimated_impact.lower(), 1)
        effort_score = {"high": 1, "medium": 2, "low": 3}.get(suggestion.estimated_effort.lower(), 1)
        
        total_score = severity_score * 2 + impact_score + effort_score
        
        if total_score >= 10:
            return "P1"
        elif total_score >= 8:
            return "P2"
        elif total_score >= 6:
            return "P3"
        else:
            return "P4"
