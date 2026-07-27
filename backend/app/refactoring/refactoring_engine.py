from pathlib import Path
from app.schemas.refactoring import RefactoringResponse, RefactoringSummary
from app.services.scanner_service import scanner_service
from app.services.framework_detector import detector_service
from app.services.dependency_graph import graph_builder
from app.parsers.parser_engine import ParserEngine
from app.analyzers.architecture_builder import architecture_builder
from app.refactoring.suggestion_generator import SuggestionGenerator
from app.refactoring.priority_ranker import PriorityRanker

class RefactoringEngine:
    """Orchestrates generation and ranking of refactoring suggestions."""
    
    def __init__(self, suggestion_generator: SuggestionGenerator, priority_ranker: PriorityRanker):
        self.suggestion_generator = suggestion_generator
        self.priority_ranker = priority_ranker

    def analyze(self, project_path: Path) -> RefactoringResponse:
        """Run all necessary analyzers and return ranked suggestions."""
        # Check if project exists
        if not project_path.exists() or not project_path.is_dir():
            raise FileNotFoundError(f"Project path not found or not a directory: {project_path}")
            
        try:
            scan_result = scanner_service.scan(project_path)
            
            # If no files, return empty early
            if scan_result.total_files == 0:
                return RefactoringResponse(
                    summary=RefactoringSummary(total_suggestions=0),
                    suggestions=[]
                )
                
            detection_result = detector_service.detect(project_path, scan_result)
            graph_result = graph_builder.build(project_path, scan_result)
            parsing_result = ParserEngine.parse_project(project_path, scan_result)
            architecture_result = architecture_builder.build(
                scan_result, detection_result, graph_result, parsing_result
            )
            
            suggestions = self.suggestion_generator.generate(
                scan_result=scan_result,
                parsing_result=parsing_result,
                graph_result=graph_result,
                architecture_result=architecture_result
            )
            
            ranked_suggestions = self.priority_ranker.rank(suggestions)
            
            return RefactoringResponse(
                summary=RefactoringSummary(total_suggestions=len(ranked_suggestions)),
                suggestions=ranked_suggestions
            )
            
        except Exception as e:
            # Re-raise for API layer to catch and return 500
            raise RuntimeError(f"Refactoring engine failed: {e}") from e

# Default instances
suggestion_generator = SuggestionGenerator()
priority_ranker = PriorityRanker()
refactoring_engine = RefactoringEngine(suggestion_generator, priority_ranker)
