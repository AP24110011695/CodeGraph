import logging
from app.schemas.planning import AIPlanResponse, PlanningTraceStep
from .query_classifier import QueryClassifier
from .retrieval_strategy import RetrievalStrategy
from .reasoning_strategy import ReasoningStrategy
from .execution_planner import ExecutionPlanner
from .planning_statistics import PlanningStatistics

logger = logging.getLogger(__name__)

class PlanningPipeline:
    """Orchestrates query classification, strategy selection, and graph generation."""
    
    def __init__(self):
        self.classifier = QueryClassifier()
        self.retrieval_strategy = RetrievalStrategy()
        self.reasoning_strategy = ReasoningStrategy()
        self.planner = ExecutionPlanner()
        self.stats = PlanningStatistics()

    def generate_plan(self, query: str) -> AIPlanResponse:
        logger.info(f"PlanningPipeline: Constructing plan for query '{query}'")
        trace = []
        
        # 1. Classification
        intent = self.classifier.classify(query)
        trace.append(PlanningTraceStep(step="Query Classification", description=f"Classified intent as {intent}"))
        
        # 2. Strategies
        retrieval = self.retrieval_strategy.determine(intent)
        trace.append(PlanningTraceStep(step="Retrieval Strategy", description=f"Selected {retrieval}"))
        
        reasoning = self.reasoning_strategy.determine(intent)
        trace.append(PlanningTraceStep(step="Reasoning Strategy", description=f"Selected {reasoning}"))
        
        # 3. Execution Graph
        modules = self.planner.plan_modules(intent)
        order = self.planner.order_modules(modules)
        cost = self.planner.estimate_cost(modules)
        trace.append(PlanningTraceStep(step="Execution Planning", description=f"Planned {len(modules)} modules with {cost} cost"))
        
        # 4. Confidence Stats
        confidence = self.stats.calculate_confidence(intent, modules)
        
        return AIPlanResponse(
            query=query,
            intent=intent,
            required_modules=modules,
            execution_order=order,
            retrieval_strategy=retrieval,
            reasoning_strategy=reasoning,
            confidence_score=confidence,
            estimated_cost=cost,
            planning_trace=trace
        )
