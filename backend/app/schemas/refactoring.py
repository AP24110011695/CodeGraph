from pydantic import BaseModel, Field

class RefactoringSuggestion(BaseModel):
    title: str = Field(..., description="Short descriptive title of the suggestion")
    category: str = Field(..., description="Category like Architecture, Code Smell, Security, etc.")
    severity: str = Field(..., description="low, medium, high, critical")
    priority: str = Field(..., description="P1, P2, P3, P4")
    reason: str = Field(..., description="Detailed reason for the suggestion")
    evidence: str = Field(..., description="Evidence from repository scan (e.g. 'UserService has 1500 lines')")
    affected_files: list[str] = Field(default_factory=list, description="Files affected by this suggestion")
    estimated_impact: str = Field(..., description="High, Medium, Low")
    estimated_effort: str = Field(..., description="High, Medium, Low")
    recommendation: str = Field(..., description="Actionable recommendation")

class RefactoringSummary(BaseModel):
    total_suggestions: int = Field(0, description="Total number of suggestions generated")

class RefactoringResponse(BaseModel):
    summary: RefactoringSummary = Field(..., description="Summary of suggestions")
    suggestions: list[RefactoringSuggestion] = Field(default_factory=list, description="List of generated suggestions")
